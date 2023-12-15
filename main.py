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
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="➕ Add me to a group",
                              url=f"tg://resolve?domain={cl.me.username}&startgroup=&admin=manage_chat+restrict_members")],
        [InlineKeyboardButton(text="➕ Add me to a channel",
                              url=f"tg://resolve?domain={cl.me.username}&startchannel&admin=change_info+restrict_members+post_messages")],
        [InlineKeyboardButton(text="📦 Public Repository", url="https://github.com/samuelmarc/kickallmembersbot")]
    ])
    await m.reply(
        f"Hello {m.from_user.mention} I am a bot to remove (not ban) all users from your group or channel created by @samuel_ks, below you can add the bot to your group or channel or access the bot's public repository .",
        reply_markup=keyboard)


@bot.on_message(filters.command("help"))
async def help_bot(_, m: Message):
    await m.reply(
        "Need help? To use the bot it's very simple, just add me to your group or channel as an admin and use the /kick_all command and all users will be removed (not banned).")


@bot.on_message(filters.command("kick_all") & (filters.channel | filters.group))
async def kick_all_members(cl: Client, m: Message):
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
            kick_count = 0
            members_count = chat.members_count
            if members_count <= 200:
                async for member in chat.get_members():
                    if member.user.id == cl.me.id:
                        continue
                    elif member.status == ChatMemberStatus.ADMINISTRATOR or member.status == ChatMemberStatus.OWNER:
                        continue
                    try:
                        await chat.ban_member(member.user.id, datetime.now() + timedelta(seconds=30))
                        kick_count += 1
                    except FloodWait as e:
                        await asyncio.sleep(e.value)
                await m.reply(f"✅ Total Users Removed: {kick_count}")
            else:
                loops_count = members_count / 200
                loops_count = round(loops_count)
                for loop_num in range(loops_count):
                    async for member in chat.get_members():
                        if member.user.id == cl.me.id:
                            continue
                        elif member.status == ChatMemberStatus.ADMINISTRATOR or member.status == ChatMemberStatus.OWNER:
                            continue
                        try:
                            await chat.ban_member(member.user.id, datetime.now() + timedelta(seconds=30))
                            kick_count += 1
                        except FloodWait as e:
                            await asyncio.sleep(e.value)
                    await asyncio.sleep(15)
                await m.reply(f"✅ Total Users Removed: {kick_count}")
        else:
            await m.reply("❌ The bot is admin but does not have the necessary permissions!")
    else:
        await m.reply("❌ The bot must have admin!")


bot.run()
