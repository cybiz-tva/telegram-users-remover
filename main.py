import asyncio
import logging
import os
from datetime import datetime, timedelta

import uvloop
from pyrogram import Client, filters
from pyrogram.enums import ChatType, ChatMemberStatus
from pyrogram.errors import FloodWait
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

# Assuming that telegramBotApi is the module you've created
from ../../telegram_bot_api.app.mjs import ban_chat_member

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
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add me to a group",
                              url=f"tg://resolve?domain={cl.me.username}&startgroup=&admin=manage_chat+restrict_members")],
        [InlineKeyboardButton(text="➕ Add me to a channel",
                              url=f"tg://resolve?domain={cl.me.username}&startchannel&admin=change_info+restrict_members+post_messages")],
        [InlineKeyboardButton(text="📦 Public Repository", url="https://github.com/cybiz-tva")]
    ])
    await m.reply(
        f"Hello {m.from_user.mention} I am a bot to remove (not ban) all users from your group or channel created by cybiz, below you can add the bot to your group or channel or access the bot's public repository.",
        reply_markup=keyboard)

@bot.on_message(filters.command("help"))
async def help_bot(_, m: Message):
    await m.reply(
        "Need help? To use the bot it's very simple, just add me to your group or channel as an admin and use the /kick_all command and all users will be removed (not banned).")

@bot.on_message(filters.command("kick_all") & (filters.channel | filters.group))
async def kick_all_members(cl: Client, m: Message):
    # Existing code for kicking all members

@bot.on_message(filters.command("remove") & (filters.channel | filters.group))
async def remove_members(cl: Client, m: Message):
    # Existing code for removing members

@bot.on_message(filters.command("kick_user") & (filters.channel | filters.group))
async def kick_user(cl: Client, m: Message):
    chat = await cl.get_chat(chat_id=m.chat.id)
    my = await chat.get_member(cl.me.id)
    
    if my.privileges:
        if my.privileges.can_manage_chat and my.privileges.can_restrict_members:
            user_id = m.text.split()[1]
            
            try:
                await ban_chat_member(chat.id, user_id)
                await m.reply(f"✅ User with ID {user_id} has been kicked.")
            except Exception as e:
                await m.reply(f"❌ Failed to kick user with ID {user_id}: {str(e)}")
        else:
            await m.reply("❌ The bot is an admin but does not have the necessary permissions!")
    else:
        await m.reply("❌ The bot must have admin!")

bot.run()
