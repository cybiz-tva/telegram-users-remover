import asyncio
import logging
import os
from datetime import datetime, timedelta

import uvloop
from pyrogram import Client, filters
from pyrogram.raw import functions
from pyrogram.raw.types import UpdateNewMessage, UpdateMessageID, UpdateMessageEdited
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


@bot.on_raw_update()
async def on_raw_update(_, update, users, chat_id):
    if isinstance(update, UpdateMessageID) or isinstance(update, UpdateNewMessage) or isinstance(update, UpdateMessageEdited):
        if hasattr(update, 'message'):
            message = update.message
            if hasattr(message, 'reactions') and len(message.reactions) > 0:
                for reaction in message.reactions:
                    if reaction.reaction == TARGET_EMOJI:
                        user_id = reaction.user_id
                        # Remove the user or take any other action
                        await remove_user(chat_id, user_id)


async def remove_user(chat_id, user_id):
    try:
        # Your code to remove or take action on the user
        await bot.kick_chat_member(chat_id, user_id)
    except Exception as e:
        logging.error(f"Error removing user: {e}")


bot.run()
