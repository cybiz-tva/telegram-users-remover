import asyncio
import logging
import os
from datetime import datetime, timedelta

import uvloop
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.raw.types import UpdateNewMessage, UpdateMessageID
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_EMOJI = "👍"  # Replace with the emoji you want to track

uvloop.install()

bot = Client(name="reactiontrackerbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.warning("⚡️ Bot Started!")


@bot.on_message(filters.command("start") & filters.private)
async def start_bot(cl, m):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="React to this message", callback_data="react")]
    ])
    await m.reply("Hello! React to the message with the specified emoji to be tracked.", reply_markup=keyboard)


@bot.on_callback_query(filters.regex("react"))
async def react_callback(_, cq):
    message = cq.message
    chat_id = message.chat.id
    message_id = message.message_id

    # Send the message to be tracked
    tracked_message = await bot.send_message(chat_id, "This message is being tracked. React to it with the specified emoji.")

    # Store the tracked message ID for future reference
    await bot.set_database(chat_id, {"tracked_message_id": tracked_message.message_id})


@bot.on_raw_reaction_add()
async def on_reaction_add(client, update, users):
    message_id = update.message_id
    chat_id = update.chat_id
    user_id = users[0]

    # Check if the reaction is on the tracked message
    tracked_message_id = await client.get_database(chat_id, "tracked_message_id")
    if message_id == tracked_message_id:
        # Remove the user or take any other action
        await remove_user(client, chat_id, user_id)


@bot.on_raw_reaction_remove()
async def on_reaction_remove(client, update, users):
    message_id = update.message_id
    chat_id = update.chat_id
    user_id = users[0]

    # Check if the reaction is on the tracked message
    tracked_message_id = await client.get_database(chat_id, "tracked_message_id")
    if message_id == tracked_message_id:
        # Remove the user or take any other action
        await remove_user(client, chat_id, user_id)


async def remove_user(client, chat_id, user_id):
    try:
        # Your code to remove or take action on the user
        await client.kick_chat_member(chat_id, user_id)
    except Exception as e:
        logging.error(f"Error removing user: {e}")


bot.run()
