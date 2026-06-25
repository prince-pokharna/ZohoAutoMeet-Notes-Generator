"""
main.py
-------
The conductor of the whole pipeline. Each time this runs (Mon-Thu, via
GitHub Actions cron), it:

  1. Reads links.json to find your 40 recording links
  2. Reads progress.json to know which day-pair to do next (1&2, then 3&4, ...)
  3. Downloads both videos, transcribes both, generates notes for both
  4. Combines both into one Word doc
  5. Hands the .docx off to the WhatsApp sender
  6. Updates progress.json so tomorrow picks up the next pair automatically
  7. Commits progress.json back to the repo (so state persists between runs)

You only ever touch links.json. Everything else is automatic.
"""

import sys
import json
from pathlib import Path

# Make the scripts folder importable
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from download_recording import download_zoho_recording
from transcribe import extract_audio, transcribe_audio
from generate_notes import generate_notes_with_groq

PROJECT_ROOT = SCRIPT_DIR.parent
LINKS_FILE = PROJECT_ROOT / "links.json"
PROGRESS_FILE = PROJECT_ROOT / "progress.json"
WORK_DIR = PROJECT_ROOT / "work"
OUTPUT_DIR = PROJECT_ROOT / "output"


def load_links() -> list[str]:
    data = json.loads(LINKS_FILE.read_text(encoding="utf-8"))
    return data["links"]  # expects {"links": ["https://...", "https://...", ...]}


def load_progress() -> int:
    """Returns the index (0-based) of the NEXT day to process.
    e.g. 0 means 'Day 1 & Day 2 haven't been done yet'."""
    if not PROGRESS_FILE.exists():
        return 0
    data = json.loads(PROGRESS_FILE.read_text(encoding="utf-8"))
    return data.get("next_day_index", 0)


def save_progress(next_index: int) -> None:
    PROGRESS_FILE.write_text(
        json.dumps({"next_day_index": next_index}, indent=2),
        encoding="utf-8",
    )


def process_one_day(link: str, day_number: int) -> str:
    """Runs download -> transcribe -> generate_notes for a single day's
    recording link. Returns the path to that day's notes JSON file."""
    day_label = f"Day {day_number}"
    video_path = WORK_DIR / f"day{day_number}.mp4"
    transcript_path = WORK_DIR / f"day{day_number}_transcript.txt"
    notes_json_path = WORK_DIR / f"day{day_number}_notes.json"

    print(f"\n===== Processing {day_label} =====")

    print(f"--> Downloading recording...")
    ok = download_zoho_recording(link, str(video_path))
    if not ok:
        raise RuntimeError(
            f"Could not download {day_label} recording. "
            f"The Zoho page structure may have changed — see README troubleshooting."
        )

    print(f"--> Extracting audio + transcribing...")
    audio_path = str(video_path.with_suffix(".wav"))
    extract_audio(str(video_path), audio_path)
    transcribe_audio(audio_path, str(transcript_path), model_size="base")
    Path(audio_path).unlink(missing_ok=True)

    print(f"--> Generating human-style notes with AI...")
    transcript_text = transcript_path.read_text(encoding="utf-8")
    notes = generate_notes_with_groq(transcript_text, day_label)
    notes_json_path.write_text(json.dumps(notes, indent=2), encoding="utf-8")

    # Free up disk space — video files are large and we don't need them anymore
    video_path.unlink(missing_ok=True)

    return str(notes_json_path)


def main():
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    links = load_links()
    next_index = load_progress()  # 0-based index of first day in today's pair

    if next_index + 1 >= len(links):
        print("All recordings have already been processed. Nothing to do today.")
        print("Add more links to links.json to continue.")
        return

    day1_number = next_index + 1       # human-friendly "Day N" numbering
    day2_number = next_index + 2

    link1 = links[next_index]
    link2 = links[next_index + 1]

    print(f"Today's pair: Day {day1_number} and Day {day2_number}")

    day1_notes_path = process_one_day(link1, day1_number)
    day2_notes_path = process_one_day(link2, day2_number)

    # Build combined Word doc
    from build_docx import build_combined_docx
    output_docx = OUTPUT_DIR / f"Notes_Day{day1_number}_Day{day2_number}.docx"
    build_combined_docx(
        day1_notes_path, day2_notes_path, str(output_docx),
        day1_label=f"Day {day1_number}", day2_label=f"Day {day2_number}",
    )

    print(f"\n===== DONE — combined notes ready at {output_docx} =====")

    # Advance progress for tomorrow
    save_progress(next_index + 2)
    print(f"Progress updated — tomorrow will process Day {day2_number + 1} & Day {day2_number + 2}")

    # Write the final output path to a known location the WhatsApp bot will read
    (PROJECT_ROOT / "latest_output_path.txt").write_text(str(output_docx), encoding="utf-8")


if __name__ == "__main__":
    main()
