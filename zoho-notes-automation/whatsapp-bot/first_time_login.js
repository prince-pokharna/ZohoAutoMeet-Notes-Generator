/**
 * first_time_login.js
 * --------------------
 * Run this ONCE, manually, on your own computer (not on GitHub Actions).
 * It shows a QR code in your terminal — scan it with WhatsApp on your
 * phone (Settings > Linked Devices > Link a Device) using your MAIN
 * number, exactly like linking WhatsApp Web in a browser.
 *
 * Once scanned, it saves a "session" folder (./wwebjs_auth) that
 * remembers the login. You then upload that session folder as a secret
 * to GitHub Actions so the automated runs can use it WITHOUT scanning
 * a QR code every time.
 *
 * Run with:  node first_time_login.js
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const qrcode = require("qrcode-terminal");

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./wwebjs_auth" }),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  },
});

client.on("qr", (qr) => {
  console.log("\n\nSCAN THIS QR CODE WITH YOUR WHATSAPP (the phone that owns your main number):\n");
  qrcode.generate(qr, { small: true });
  console.log("\nOn your phone: WhatsApp > Settings > Linked Devices > Link a Device\n");
});

client.on("ready", () => {
  console.log("\n✅ Logged in successfully!");
  console.log("Session saved in ./wwebjs_auth — this folder is your login.");
  console.log("Next step: zip this folder and add it as a GitHub Actions secret.");
  console.log("See README.md section 'Step 5' for exact instructions.\n");
  process.exit(0);
});

client.on("auth_failure", (msg) => {
  console.error("Authentication failed:", msg);
  process.exit(1);
});

client.initialize();
