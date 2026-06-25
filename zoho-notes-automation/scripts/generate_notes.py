"""
generate_notes.py
------------------
Takes a raw transcript (messy spoken text) and turns it into clean,
structured, human-style study notes using a free LLM API (Groq).

Why Groq: free tier, no credit card, generous enough for 2 calls/day,
and very fast. Get a free key at https://console.groq.com

If Groq ever gives you trouble, this file also has a Gemini fallback
function you can switch to with one line (see bottom of file).

Usage:
    python generate_notes.py <transcript_txt_path> <day_label> <output_json_path>

Example:
    python generate_notes.py day1_transcript.txt "Day 1" day1_notes.json
"""

import sys
import os
import json
from pathlib import Path


NOTES_SYSTEM_PROMPT = """You are an excellent student who takes beautiful, clear, \
human-style handwritten-feel notes from lecture transcripts. You are NOT a \
transcription summarizer that lists facts in dry bullet form — you write notes \
the way a top student would, in their own organized words, easy to revise from.

Rules for the notes you produce:
1. Organize into clear sections with short, descriptive headings (not "Section 1" \
   but actual topic names like "Introduction to Supply and Demand").
2. Under each heading, use a mix of short paragraphs and bullet points — whichever \
   communicates the idea better. Avoid robotic bullet-only structure.
3. Bold the key terms and definitions a student would want to highlight.
4. Include a short "Key Takeaways" list at the very end (3-6 points).
5. If the transcript mentions examples, keep them — examples are gold for revision.
6. Fix filler words, false starts, and spoken-language artifacts from the \
   transcript ("um", "so basically", "right so") — write in clean written English, \
   but keep the actual teaching content, explanations and examples complete. \
   Do not skip content to save space; this should be thorough, 3-4 pages worth.
7. Do NOT invent any content that wasn't in the transcript.

Output strictly as JSON with this exact structure, nothing else, no markdown \
fences, no commentary:
{
  "title": "<a short descriptive title for this session>",
  "sections": [
    {"heading": "<heading text>", "content": "<paragraph and/or bullet content as a single string, use \\n for line breaks and '- ' prefix for bullet lines>"}
  ],
  "key_takeaways": ["<point 1>", "<point 2>", "..."]
}
"""


def generate_notes_with_groq(transcript: str, day_label: str) -> dict:
    from groq import Groq

    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY environment variable is not set.")

    client = Groq(api_key=api_key)

    user_prompt = f"""This is the transcript for "{day_label}" of a course/training.
Turn it into well-structured human-style notes following the system instructions.

TRANSCRIPT:
{transcript}
"""

    print(f"   Sending transcript to Groq (Llama 3.3 70B) for note generation...")
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": NOTES_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
        max_tokens=8000,
        response_format={"type": "json_object"},
    )

    raw = response.choices[0].message.content
    return json.loads(raw)


def generate_notes_with_gemini(transcript: str, day_label: str) -> dict:
    """
    FALLBACK OPTION — use this if Groq's free tier ever isn't enough.
    Requires: pip install google-generativeai
    Get a free key at https://aistudio.google.com/app/apikey
    To switch: in main(), change generate_notes_with_groq(...) to
    generate_notes_with_gemini(...)
    """
    import google.generativeai as genai

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is not set.")

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        "gemini-2.0-flash",
        system_instruction=NOTES_SYSTEM_PROMPT,
    )

    user_prompt = f"""This is the transcript for "{day_label}".
TRANSCRIPT:
{transcript}
"""
    response = model.generate_content(
        user_prompt,
        generation_config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)


def main():
    if len(sys.argv) != 4:
        print("Usage: python generate_notes.py <transcript_txt_path> <day_label> <output_json_path>")
        sys.exit(1)

    transcript_path, day_label, output_json_path = sys.argv[1], sys.argv[2], sys.argv[3]
    transcript = Path(transcript_path).read_text(encoding="utf-8")

    if not transcript.strip():
        raise RuntimeError(f"Transcript at {transcript_path} is empty.")

    notes = generate_notes_with_groq(transcript, day_label)

    Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
    Path(output_json_path).write_text(json.dumps(notes, indent=2), encoding="utf-8")
    print(f"   Notes JSON saved to {output_json_path}")


if __name__ == "__main__":
    main()
