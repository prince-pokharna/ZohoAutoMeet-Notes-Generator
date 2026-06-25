"""
transcribe.py
-------------
Takes a downloaded meeting video, extracts just the audio (smaller + faster
to process), then runs it through a local Whisper model to get text.

100% free, no API key, no internet needed for this step (after first model
download). Uses faster-whisper, which is a much faster re-implementation
of OpenAI's Whisper that still runs fine on a regular CPU.

Usage:
    python transcribe.py <video_path> <output_txt_path>
"""

import sys
import subprocess
from pathlib import Path


def extract_audio(video_path: str, audio_path: str) -> None:
    """Pull just the audio track out of the video using ffmpeg, as a 16kHz
    mono WAV (the format Whisper wants — smaller file, faster processing)."""
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vn",                  # no video
        "-acodec", "pcm_s16le",
        "-ar", "16000",         # 16kHz sample rate
        "-ac", "1",             # mono
        audio_path,
    ]
    print(f"[1/2] Extracting audio from {video_path} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"ffmpeg failed:\n{result.stderr}")
    print(f"   Audio extracted to {audio_path}")


def transcribe_audio(audio_path: str, output_txt_path: str, model_size: str = "base") -> str:
    """
    model_size options (bigger = more accurate but slower):
      "tiny"   -> fastest, least accurate, ~1GB RAM
      "base"   -> good balance for clear meeting audio, ~1GB RAM   <-- default
      "small"  -> noticeably better accuracy, ~2GB RAM
      "medium" -> best accuracy, slow on CPU, ~5GB RAM
    """
    from faster_whisper import WhisperModel

    print(f"[2/2] Loading Whisper model ({model_size})... this can take a minute on first run.")
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    print("   Transcribing (this is the slow part — grab a coffee)...")
    segments, info = model.transcribe(audio_path, beam_size=5)

    full_text = []
    for segment in segments:
        full_text.append(segment.text.strip())

    transcript = " ".join(full_text)

    Path(output_txt_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_txt_path).write_text(transcript, encoding="utf-8")

    print(f"   Transcript saved to {output_txt_path} ({len(transcript)} characters)")
    return transcript


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python transcribe.py <video_path> <output_txt_path>")
        sys.exit(1)

    video_path = sys.argv[1]
    output_txt_path = sys.argv[2]
    audio_path = str(Path(video_path).with_suffix(".wav"))

    extract_audio(video_path, audio_path)
    transcribe_audio(audio_path, output_txt_path)

    # Clean up the intermediate audio file to save disk space
    Path(audio_path).unlink(missing_ok=True)
