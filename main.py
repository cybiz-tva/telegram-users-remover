import asyncio
import logging
from datetime import datetime, timedelta

import uvloop
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNEL_ID = int(os.getenv("CHANNEL_ID"))  # Replace with your channel ID
INACTIVITY_PERIOD = timedelta(days=30)  # Adjust inactivity threshold as needed


uvloop.install()

bot = Client(name="reactiontrackerbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.warning("⚡️ Bot Started!")


@bot.on_message(filters.chat(CHANNEL_ID) & ~filters.service())  # Listen for non-service messages in the channel
async def track_channel_messages(cl, m):
    global last_message_id
    last_message_id = m.message_id


async def track_reactions():
    global last_message_id
    last_reacted_users = set()  # Store IDs of users who reacted to the last message

    while True:
        latest_message = await bot.get_messages(CHANNEL_ID, limits=1)
        # Check if last message has changed
        if latest_message and last_message_id != latest_message[0].message_id:
            last_message_id = latest_message[0].message_id
            # Clear previous reaction data and start tracking new message
            last_reacted_users.clear()
            continue

        reactions = await bot.get_reactions(chat_id=CHANNEL_ID, message_id=last_message_id)
        for user_id in reactions.users:
            last_reacted_users.add(user_id)

        inactive_users = set()  # Identify users who haven't reacted for the inactivity period
        for member in await bot.get_chat_members(CHANNEL_ID):
            member_id = member.user.id
            if member_id not in last_reacted_users:
                inactive_time = datetime.now() - member.joined_date
                if inactive_time > INACTIVITY_PERIOD:
                    inactive_users.add(member_id)

        # Implement your logic for handling inactive users (e.g., warnings, reminders, or removal)
        # You should offer alternative engagement methods and opting-out options before removal
        # for user_id in inactive_users:
        #     await bot.kick_chat_member(CHANNEL_ID, user_id)

        await asyncio.sleep(60)  # Adjust polling interval as needed


# Start tracking reactions and channel messages
bot.loop.create_task(track_reactions())
bot.loop.create_task(track_channel_messages())

bot.run()
