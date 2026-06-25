/**
 * list_groups.js
 * --------------
 * Run this ONCE after first_time_login.js, on your own computer, to find
 * the exact ID of your WhatsApp group. You need this ID for send_to_whatsapp.js.
 *
 * Run with:  node list_groups.js
 */

const { Client, LocalAuth } = require("whatsapp-web.js");
const { sharedClientOptions } = require("./client_config");

const client = new Client({
  ...sharedClientOptions,
  authStrategy: new LocalAuth({ dataPath: "./wwebjs_auth" }),
});

client.on("ready", async () => {
  console.log("Client ready. Waiting a moment before fetching chats...\n");
  // A short pause after "ready" gives WhatsApp Web's internal state time to
  // fully settle — fetching chats immediately is a common trigger for the
  // Runtime.callFunctionOn timeout on some Windows setups.
  await new Promise((r) => setTimeout(r, 5000));

  try {
    console.log("Fetching your chats...\n");
    const chats = await client.getChats();
    const groups = chats.filter((chat) => chat.isGroup);

    console.log("===== YOUR WHATSAPP GROUPS =====\n");
    groups.forEach((g) => {
      console.log(`Name: ${g.name}`);
      console.log(`ID:   ${g.id._serialized}`);
      console.log("---");
    });

    console.log(`\nFound ${groups.length} groups.`);
    console.log("Copy the ID of the group you want notes sent to, and paste it");
    console.log("into send_to_whatsapp.js as the GROUP_ID value.\n");

    process.exit(0);
  } catch (err) {
    console.error("\n❌ Failed to fetch chats:", err.message);
    console.error("This is a known whatsapp-web.js issue on some Windows setups.");
    console.error("Try running this script again — it sometimes succeeds on a");
    console.error("second attempt once WhatsApp Web's cache has settled.");
    console.error("If it keeps failing, see README.md Troubleshooting section.\n");
    process.exit(1);
  }
});

client.initialize();
