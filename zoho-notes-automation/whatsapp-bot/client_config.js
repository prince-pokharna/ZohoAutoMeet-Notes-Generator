/**
 * client_config.js
 * -----------------
 * Shared WhatsApp client settings used by all three scripts
 * (first_time_login.js, list_groups.js, send_to_whatsapp.js).
 *
 * WHY THIS FILE EXISTS:
 * whatsapp-web.js works by injecting code into the real WhatsApp Web site.
 * When WhatsApp updates their site faster than the library catches up, that
 * injection can hang and throw:
 *   "ProtocolError: Runtime.callFunctionOn timed out"
 * This is a known, recurring issue (see github.com/wwebjs/whatsapp-web.js
 * issues #127050, #5733, #3076, #5682 — same error, same root cause).
 *
 * THE FIX (used by the library's own community as the standard workaround):
 * Pin WhatsApp Web to a specific, known-stable version instead of letting
 * it load whatever the absolute latest is. The wppconnect-team maintains a
 * public archive of known-good versions specifically for this purpose.
 *
 * If THIS pinned version ever stops working (WhatsApp eventually retires
 * old versions), check https://github.com/wppconnect-team/wa-version for a
 * newer known-good version number and update WA_VERSION below.
 */

const WA_VERSION = "2.2412.54"; // known-stable version, update if needed (see comment above)

const sharedClientOptions = {
  puppeteer: {
    headless: true,
    args: [
      "--no-sandbox",
      "--disable-setuid-sandbox",
      "--disable-dev-shm-usage", // helps avoid crashes in low-memory/cloud environments
    ],
    // Give the browser <-> Node communication much more breathing room.
    // Default is 30s, which is too tight for slower machines or first-time
    // loads. This does NOT fix a genuine version mismatch by itself, but
    // combined with the pinned version below it resolves the timeout for
    // most people.
    protocolTimeout: 120000, // 120 seconds
  },
  webVersionCache: {
    type: "remote",
    remotePath: `https://raw.githubusercontent.com/wppconnect-team/wa-version/main/html/${WA_VERSION}.html`,
  },
};

module.exports = { sharedClientOptions, WA_VERSION };
