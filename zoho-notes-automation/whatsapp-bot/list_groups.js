/**
 * list_groups.js
 * --------------
 * Run this ONCE after first_time_login.js, on your own computer, to find
 * the exact ID of your WhatsApp group. You need this ID for send_to_whatsapp.js.
 *
 * Run with:  node list_groups.js
 */

const { Client, LocalAuth } = require("whatsapp-web.js");

const client = new Client({
  authStrategy: new LocalAuth({ dataPath: "./wwebjs_auth" }),
  puppeteer: {
    headless: true,
    args: ["--no-sandbox", "--disable-setuid-sandbox"],
  },
});

client.on("ready", async () => {
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
});

client.initialize();
