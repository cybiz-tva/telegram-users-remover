import os
import asyncio
import logging
from datetime import datetime, timedelta

from pyrogram import Client, filters

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Use channel ID if available
CHANNEL_ID = int(os.getenv("CHANNEL_ID")) if os.getenv("CHANNEL_ID") else None

# Use channel username if ID is not available
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME") if not CHANNEL_ID else None

INACTIVITY_PERIOD = timedelta(days=30)  # Adjust inactivity threshold as needed

bot = Client(name="reactiontrackerbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

last_message_id = None  # Stores the ID of the last tracked message
active_users = set()  # Tracks users who reacted to the last message
inactive_warnings = set()  # Tracks users warned about inactivity


@bot.on_message(filters.command("join") & filters.chat(CHANNEL_ID))
async def join_channel_command(_, m):
    global last_message_id, active_users, inactive_warnings
    last_message_id = None
    active_users.clear()
    inactive_warnings.clear()
    await m.reply("Tracking started! Users who haven't reacted to the last message in 30 days might be warned (you can opt-out with /leave).")
    if not CHANNEL_ID:
        CHANNEL_ID = await get_channel_id(CHANNEL_USERNAME)  # Fetch channel ID using username if needed
    bot.loop.create_task(track_reactions())

@bot.on_message(filters.command("leave") & filters.chat(CHANNEL_ID))
async def leave_channel_command(_, m):
    global active_users, inactive_warnings
    active_users.discard(m.from_user.id)
    inactive_warnings.discard(m.from_user.id)
    await m.reply("You've opted out of tracking. You won't receive further warnings.")

@bot.on_message(filters.chat(CHANNEL_ID) & ~filters.service())  # Listen for non-service messages in the channel
async def track_channel_messages(_, m):
    global last_message_id
    last_message_id = m.message_id

async def track_reactions():
    global last_message_id, active_users, inactive_warnings
    while True:
        latest_message = await bot.get_messages(CHANNEL_ID, limit=1)
        # Check if the last message has changed
        if latest_message and last_message_id != latest_message[0].message_id:
            last_message_id = latest_message[0].message_id
            # Clear previous reaction data and start tracking the new message
            active_users.clear()
            inactive_warnings.clear()

        reactions = await bot.get_reactions(chat_id=CHANNEL_ID, message_id=last_message_id)
        for user_id in reactions.users:
            active_users.add(user_id)

        inactive_users = set()  # Identify users who haven't reacted for the inactivity period
        for member in await bot.get_chat_members(CHANNEL_ID):
            member_id = member.user.id
            if member_id not in active_users:
                inactive_time = datetime.now() - member.joined_date
                if inactive_time > INACTIVITY_PERIOD:
                    inactive_users.add(member_id)

        # Warn users who haven't been warned before about potential removal
        for user_id in inactive_users.difference(inactive_warnings):
            await bot.send_message(chat_id=CHANNEL_ID,
                                   text=f"Hi <mention here>, you haven't reacted to the last message in a while. Consider engaging to stay active in the community.")
            # Add the user to the set of warned users
            inactive_warnings.add(user_id)

        await asyncio.sleep(60)  # Adjust the polling interval as needed

if __name__ == "__main__":
    bot.run()
