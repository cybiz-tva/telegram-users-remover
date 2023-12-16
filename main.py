import asyncio
import logging
import os
from datetime import datetime, timedelta

import uvloop
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

uvloop.install()

bot = Client(name="kickmemberbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.warning("⚡️ Bot Started!")


@bot.on_message(filters.command("start") & filters.private)
async def start_bot(cl: Client, m: Message):
    # Your existing start command code

@bot.on_message(filters.command("help"))
async def help_bot(_, m: Message):
    """
    Provides help information about the bot's available commands.
    """
    await m.reply(
        "Available commands:\n"
        "- /start: Start the bot and get information\n"
        "- /kick_all: Kick all members (admins only, in channels/groups)\n"
        "- /remove <user_id>: Remove a specific user (admins only, in channels/groups)"
    )

@bot.on_message(filters.command("kick_all") & (filters.channel | filters.group))
async def kick_all_members(cl: Client, m: Message):
    # Your existing kick_all_members command code

@bot.on_message(filters.command("remove") & (filters.channel | filters.group))
async def remove_members(cl: Client, m: Message):
    """
    Removes a specific member from a channel or group.
    Args:
        cl: The Pyrogram client object.
        m: The message object containing the command and user ID.
    """

    chat = await cl.get_chat(chat_id=m.chat.id)
    my = await chat.get_member(cl.me.id)

    if my.privileges:
        if my.privileges.can_manage_chat and my.privileges.can_restrict_members:
            is_channel = True if m.chat.type == ChatType.CHANNEL else False
            if not is_channel:
                req_user_member = await chat.get_member(m.from_user.id)
                if req_user_member.privileges is None:
                    await m.reply("❌ You are not admin and cannot execute this command!")
                    return

            args = m.text.split(" ")
            if len(args) != 2 or not args[1].isdigit():
                await m.reply("❌ Please provide a valid user ID to remove.")
                return

            user_id_to_remove = int(args[1])
            try:
                await chat.kick_member(user_id_to_remove, datetime.now() + timedelta(seconds=30))
                await m.reply(f"✅ User {user_id_to_remove} removed successfully!")
            except FloodWait as e:
                await asyncio.sleep(e.value)
                await m.reply(f"✅ User {user_id_to_remove} removed successfully!")
        else:
            await m.reply("❌ The bot is admin but does not have the necessary permissions!")
    else:
        await m.reply("❌ The bot must have admin privileges to remove members!")

bot.run()
