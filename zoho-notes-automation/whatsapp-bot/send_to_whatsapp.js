/**
 * send_to_whatsapp.js
 * --------------------
 * Runs on GitHub Actions (or anywhere) AFTER the Python pipeline has
 * produced the day's combined .docx. Logs into the already-authenticated
 * WhatsApp Web session (no QR code needed — session was saved earlier)
 * and sends the Word doc into your group, with a friendly caption.
 *
 * Reads the file path from ../latest_output_path.txt (written by main.py)
 *
 * Run with:  node send_to_whatsapp.js
 */

const fs = require("fs");
const path = require("path");
const { Client, LocalAuth, MessageMedia } = require("whatsapp-web.js");

// ====== EDIT THIS ======
// Paste the group ID you got from list_groups.js (looks like "1234567890-1234567890@g.us")
const GROUP_ID = "PASTE_YOUR_GROUP_ID_HERE@g.us";
// ========================

const OUTPUT_PATH_FILE = path.join(__dirname, "..", "latest_output_path.txt");

function getCaption(docxFileName) {
  // Pulls "Day 5" and "Day 6" style numbers out of filenames like
  // "Prince Pokharna (Day 5 and Day 6).docx" for a nice caption
  const match = docxFileName.match(/Day (\d+) and Day (\d+)/);
  if (match) {
    return `📘 Notes for Day ${match[1]} & Day ${match[2]} are ready! Have a great revision 🙌`;
  }
  return "📘 Today's notes are ready!";
}

async function main() {
  if (!fs.existsSync(OUTPUT_PATH_FILE)) {
    console.error(`Could not find ${OUTPUT_PATH_FILE}. Did main.py run successfully?`);
    process.exit(1);
  }

  const docxPath = fs.readFileSync(OUTPUT_PATH_FILE, "utf-8").trim();
  if (!fs.existsSync(docxPath)) {
    console.error(`Notes file not found at: ${docxPath}`);
    process.exit(1);
  }

  console.log(`Preparing to send: ${docxPath}`);

  const client = new Client({
    authStrategy: new LocalAuth({ dataPath: path.join(__dirname, "wwebjs_auth") }),
    puppeteer: {
      headless: true,
      args: ["--no-sandbox", "--disable-setuid-sandbox"],
    },
  });

  client.on("ready", async () => {
    try {
      console.log("WhatsApp client ready. Sending file...");

      const media = MessageMedia.fromFilePath(docxPath);
      const caption = getCaption(path.basename(docxPath));

      // Small human-like delay so the bot doesn't fire instantly on login —
      // reduces automated-pattern footprint.
      await new Promise((r) => setTimeout(r, 5000));

      await client.sendMessage(GROUP_ID, media, { caption });

      console.log("✅ Sent successfully to the group.");
      process.exit(0);
    } catch (err) {
      console.error("Failed to send message:", err);
      process.exit(1);
    }
  });

  client.on("auth_failure", (msg) => {
    console.error("Auth failure — session may have expired. Re-run first_time_login.js locally and re-upload the secret.", msg);
    process.exit(1);
  });

  client.initialize();
}

main();
