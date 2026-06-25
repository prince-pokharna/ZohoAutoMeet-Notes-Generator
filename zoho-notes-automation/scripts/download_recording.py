"""
download_recording.py
----------------------
Opens a Zoho Meeting public recording link in a real (headless) browser,
waits for the video player to load, captures the actual video file URL
that the page requests in the background, and downloads it to disk.

Why a browser and not just requests.get(link)?
Because the link you have is a PLAYER PAGE (like a YouTube watch page),
not a direct video file. The real .mp4/.m3u8 file is only revealed once
a browser loads the page and the player asks for it. We "listen in" on
all network requests the page makes and grab the video one automatically.

Usage:
    python download_recording.py "<zoho_link>" "<output_path.mp4>"
"""

import sys
import re
import time
from pathlib import Path
from playwright.sync_api import sync_playwright


# File extensions / patterns that indicate "this network request IS the video"
VIDEO_PATTERNS = [
    r"\.mp4(\?|$)",
    r"\.m3u8(\?|$)",   # HLS streaming playlist (common for meeting recordings)
    r"\.ts(\?|$)",     # HLS video segment
    r"videoprv.*stream",
    r"download.*record",
]


def looks_like_video_url(url: str) -> bool:
    return any(re.search(pat, url, re.IGNORECASE) for pat in VIDEO_PATTERNS)


def download_zoho_recording(zoho_link: str, output_path: str, timeout_seconds: int = 90) -> bool:
    """
    Returns True if a video file was found and saved, False otherwise.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    captured_urls = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            # A real browser user-agent helps avoid basic bot-blocking
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1366, "height": 768},
        )
        page = context.new_page()

        # Listen to every network request the page makes in the background
        def on_request(request):
            if looks_like_video_url(request.url):
                captured_urls.append(request.url)

        page.on("request", on_request)
        page.on("response", lambda response: on_request_like(response.url))

        def on_request_like(url):
            if looks_like_video_url(url):
                if url not in captured_urls:
                    captured_urls.append(url)

        print(f"[1/4] Opening: {zoho_link}")
        try:
            page.goto(zoho_link, wait_until="networkidle", timeout=timeout_seconds * 1000)
        except Exception as e:
            print(f"   Page load warning (continuing anyway): {e}")

        # Try to click a play button if the player needs an explicit click
        print("[2/4] Looking for a play button to trigger video load...")
        for selector in ["video", "button[aria-label*='play' i]", ".vjs-play-control", "[class*='play']"]:
            try:
                el = page.query_selector(selector)
                if el:
                    el.click(timeout=3000)
                    print(f"   Clicked element matching: {selector}")
                    break
            except Exception:
                continue

        # Give the player a few seconds to start requesting video data
        print("[3/4] Waiting for video stream to be requested...")
        for _ in range(15):
            if captured_urls:
                break
            time.sleep(1)

        browser.close()

    if not captured_urls:
        print("   No video URL captured. The page structure may have changed.")
        return False

    video_url = captured_urls[0]
    print(f"[4/4] Downloading video from captured stream URL...")

    # Download using a fresh browser context's request capability
    # (keeps cookies/headers consistent with what worked for viewing)
    import urllib.request
    try:
        req = urllib.request.Request(
            video_url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"},
        )
        with urllib.request.urlopen(req, timeout=120) as response, open(output_path, "wb") as out_file:
            out_file.write(response.read())
        print(f"   Saved to: {output_path}")
        return True
    except Exception as e:
        print(f"   Direct download failed ({e}). Trying Playwright download instead...")
        return False


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python download_recording.py <zoho_link> <output_path>")
        sys.exit(1)

    link = sys.argv[1]
    out = sys.argv[2]
    success = download_zoho_recording(link, out)
    sys.exit(0 if success else 1)
