# Zoho Recording → Notes → WhatsApp Automation

This system automatically, every Monday–Thursday:
1. Downloads 2 Zoho meeting recordings (the next un-processed pair)
2. Transcribes them (free, local Whisper AI)
3. Turns the transcript into clean, human-style notes (free Groq AI)
4. Combines both days into one nicely formatted Word document
5. Sends that Word document into your WhatsApp group automatically

Runs entirely on GitHub's free cloud servers. You do not need to keep your
own computer on. Total cost: **₹0**, using only free tiers.

---

## Before you start — what you need

- A GitHub account (free) — github.com
- A Groq account (free, no credit card) — console.groq.com
- Your phone with WhatsApp (your main number, since that's what you chose)
- About 30–45 minutes for the one-time setup
- A computer (Windows/Mac/Linux) for the *one-time* WhatsApp login step only

---

## ⚠️ Please read before you build this

This automation drives your **real WhatsApp account** through an
unofficial, non-Meta-sanctioned method (`whatsapp-web.js`) because there is
no official free way to post into a normal group chat. It's free and widely
used, but there's a small standing risk WhatsApp could flag heavy automated
use on a number. To keep risk low:
- The bot only sends **1 message, 1 time per day, 4 days a week** — a very
  light, human-like pattern, not a high-volume bot.
- Don't add other automated sending on top of this on the same number.
- If you ever see warnings in your WhatsApp app, stop the automation and
  investigate before continuing.

If this risk is unacceptable to you, the only fully "by-the-book" fix is
sending into a private 1:1 chat with yourself instead of a group (technically
still the same library, but lower visibility) — or manually forwarding the
doc to the group yourself each day after the bot DMs it to you. Just say so
and I'll adjust the code.

---

## PART 1 — Get your free AI key (5 minutes)

1. Go to **https://console.groq.com**
2. Sign up with Google or email (no credit card asked)
3. Click **API Keys** in the left sidebar → **Create API Key**
4. Copy the key somewhere safe (looks like `gsk_...`) — you'll paste it into
   GitHub in Part 3.

---

## PART 2 — Put the project on GitHub (10 minutes)

1. Go to **https://github.com/new**
2. Name the repository something like `notes-automation`
3. Set it to **Private** (important — your links/notes shouldn't be public)
4. Click **Create repository**
5. On your computer, open a terminal/command prompt in this project folder
   (the one containing this README) and run:

```bash
git init
git add .
git commit -m "Initial setup"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/notes-automation.git
git push -u origin main
```

(Replace `YOUR_USERNAME` with your actual GitHub username — GitHub shows you
this exact command on the empty repo page too.)

---

## PART 3 — Add your secret keys to GitHub (5 minutes)

Secrets keep your API key safe — they're encrypted and never shown in logs.

1. On your repo's GitHub page, click **Settings** → **Secrets and variables**
   → **Actions**
2. Click **New repository secret**
3. Add this one now:
   - Name: `GROQ_API_KEY`
   - Value: paste the key from Part 1
4. Click **Add secret**

(We'll add one more secret, `WHATSAPP_SESSION_B64`, in Part 5 — it needs to
be generated first.)

---

## PART 4 — Add your 44 recording links (5 minutes)

1. Open `links.json` in this project
2. Replace the example links with **all 44** real Zoho links, **in order**
   (Day 1 first, Day 2 second, ... Day 44 last) — yes, include Day 1 and
   Day 2 too, even though you already sent those manually. `progress.json`
   is already set to skip them and start the automation from Day 3 & Day 4
   — you just need the full, correctly-ordered list of 44 so the day
   numbering lines up.
3. Save the file
4. Push the change to GitHub:

```bash
git add links.json
git commit -m "Add recording links"
git push
```

The automation always works through `links.json` two-at-a-time, in order,
and remembers where it left off using `progress.json` — you never need to
tell it which day to do next.

**Adding more links later:** just edit `links.json` the same way whenever
you have new recordings, and push. No other changes needed.

---

## PART 5 — One-time WhatsApp login (10 minutes, do this on your own computer)

This is the only step that needs a real browser and your phone — but it's
**one-time only**. After this, the cloud automation runs forever without
you touching your phone again (until the session naturally expires after
weeks/months, at which point you just repeat this part).

1. Make sure you have **Node.js** installed on your computer
   (download from https://nodejs.org if not — get the "LTS" version)
2. Open a terminal in the `whatsapp-bot` folder:
   ```bash
   cd whatsapp-bot
   npm install
   ```
3. Run the login script:
   ```bash
   node first_time_login.js
   ```
4. A QR code will appear in your terminal. On your phone:
   **WhatsApp → Settings → Linked Devices → Link a Device** → scan the QR code
5. Once it says "✅ Logged in successfully!", you're done with this part.
   A new folder `whatsapp-bot/wwebjs_auth` now contains your login session.

### Find your group's ID

6. Still in the `whatsapp-bot` folder, run:
   ```bash
   node list_groups.js
   ```
7. It prints all your WhatsApp groups with their names and IDs. Find your
   target group and copy its ID (looks like `1234567890-1234567890@g.us`)
8. Open `whatsapp-bot/send_to_whatsapp.js` and replace:
   ```js
   const GROUP_ID = "PASTE_YOUR_GROUP_ID_HERE@g.us";
   ```
   with your actual group ID.

### Upload the session to GitHub (so the cloud robot can use it)

9. Zip the session folder:
   ```bash
   # Mac/Linux:
   zip -r session.zip wwebjs_auth

   # Windows (PowerShell):
   Compress-Archive -Path wwebjs_auth -DestinationPath session.zip
   ```
10. Convert it to base64 text (GitHub Secrets only accept text, not files):
    ```bash
    # Mac/Linux:
    base64 -i session.zip -o session_b64.txt

    # Windows (PowerShell):
    [Convert]::ToBase64String([IO.File]::ReadAllBytes("session.zip")) | Out-File session_b64.txt
    ```
11. Open `session_b64.txt`, copy **all** the text inside it
12. Back on GitHub: **Settings → Secrets and variables → Actions → New
    repository secret**
    - Name: `WHATSAPP_SESSION_B64`
    - Value: paste the long base64 text
13. Click **Add secret**

14. **Delete `session.zip` and `session_b64.txt` from your computer** — you
    don't need them anymore and they contain your login session.

15. Commit the `send_to_whatsapp.js` change (with your group ID in it):
    ```bash
    cd ..
    git add whatsapp-bot/send_to_whatsapp.js
    git commit -m "Add WhatsApp group ID"
    git push
    ```

**Important:** Never commit the `wwebjs_auth` folder itself to GitHub (only
the base64 secret). A `.gitignore` is included to prevent this by accident.

---

## PART 6 — Test it manually before trusting the schedule (5 minutes)

1. On GitHub, go to your repo → **Actions** tab
2. Click **Daily Notes Automation** in the left list
3. Click **Run workflow** (top right) → **Run workflow** button
4. Watch it run — click into the running job to see live logs
5. It takes anywhere from 5–25 minutes depending on video length (Whisper
   transcription is the slow part)
6. If it succeeds, check your WhatsApp group — the Word doc should appear!

If something fails, click the red ❌ step to read the error — see
Troubleshooting below for the most likely culprits.

---

## PART 7 — Let it run automatically

That's it — you're done. The schedule in
`.github/workflows/daily_notes.yml` is already set to run **Monday through
Thursday**, skipping Friday, Saturday, and Sunday, exactly as you asked.

**To change the time it runs:** open `.github/workflows/daily_notes.yml`
and edit this line:
```yaml
- cron: "30 3 * * 1-4"
```
This is in **UTC**. The example (`30 3`) = 3:30 AM UTC = **9:00 AM IST**.
To run at a different IST time, subtract 5 hours 30 minutes from your
desired IST time to get the UTC cron time.

---

## How the "which day pair is next" logic works

- `progress.json` stores a single number: the index of the next unprocessed
  day.
- Each successful run processes that day and the one after it, then
  increments the number by 2, and commits the updated file back to the repo.
- This means the system is self-tracking — you genuinely never have to tell
  it "today do day 5 and 6." It just knows.
- If a run ever fails partway, `progress.json` is only updated on full
  success, so a failed day won't get silently skipped — it'll retry the
  same pair next scheduled run (or you can re-trigger manually from the
  Actions tab).

**Output filename format:** each run produces
`Prince Pokharna (Day X and Day Y).docx` — e.g. `Prince Pokharna (Day 3 and
Day 4).docx`, then `Prince Pokharna (Day 5 and Day 6).docx`, and so on. This
is generated automatically from the day numbers; you never need to type it.

**Already-sent days:** `progress.json` ships set to `"next_day_index": 2`,
which means the automation starts from **Day 3 & Day 4** — Day 1 & Day 2 are
treated as already done, since you sent those manually before setting this
up.

---

## Troubleshooting

**"Could not download recording" / video capture fails**
Zoho occasionally changes how their player page loads the video. Open the
failing link yourself in a normal browser, right-click the video, see if
"Inspect" shows the network requests — the script in
`scripts/download_recording.py` may need its `VIDEO_PATTERNS` list updated
to match whatever new URL pattern Zoho is using. This is the single most
likely thing to need a tweak over time, since it depends on a website you
don't control.

**WhatsApp messages stop sending after a few weeks**
WhatsApp Web sessions can expire. Just repeat **Part 5** (re-scan QR, re-zip,
re-upload the secret) — takes 10 minutes.

**Groq API errors about rate limits**
You're only using 2 calls a day, so this is unlikely, but if it happens,
switch to the Gemini fallback already written in `generate_notes.py` —
get a free key at https://aistudio.google.com/app/apikey, add it as a
`GEMINI_API_KEY` secret, and swap the function call in `scripts/main.py`.

**Transcription seems inaccurate**
Open `scripts/main.py` and change `model_size="base"` to `model_size="small"`
in the `transcribe_audio(...)` call — slower but noticeably more accurate.
GitHub's free runners have enough RAM for this comfortably.

**Want to reprocess a day you already did**
Edit `progress.json` and set `next_day_index` back to the number you want
(0 = Day 1&2, 2 = Day 3&4, 4 = Day 5&6, etc. — the current default is 2,
since Day 1 & 2 were already sent manually), then commit and push, or just
trigger the workflow manually.

---

## File map (what does what)

```
notes-automation/
├── links.json                  ← YOU edit this: your 44 recording links
├── progress.json               ← auto-managed: tracks which day is next
├── requirements.txt            ← Python dependencies
├── .github/workflows/
│   └── daily_notes.yml         ← the cloud schedule (Mon-Thu trigger)
├── scripts/
│   ├── main.py                 ← orchestrates the whole pipeline
│   ├── download_recording.py   ← grabs video from Zoho link
│   ├── transcribe.py           ← video → audio → text (Whisper)
│   ├── generate_notes.py       ← text → structured notes (Groq AI)
│   └── build_docx.py           ← notes → formatted Word document
└── whatsapp-bot/
    ├── first_time_login.js     ← YOU run once: scan QR to log in
    ├── list_groups.js          ← YOU run once: find your group's ID
    └── send_to_whatsapp.js     ← auto-runs: sends the docx to your group
```
