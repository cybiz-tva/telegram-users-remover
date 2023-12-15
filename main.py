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
        [InlineKeyboardButton(text=" Public Repository", url="https://github.com/samuelmarc/kickallmembersbot")]
    ])
    await m.reply(
        f"Hello {m.from_user.mention} I am a tool to help manage your group or channel. I can remove inactive members who haven't been seen for at least 5 days. To learn more, use the /help command.",
        reply_markup=keyboard)


@bot.on_message(filters.command("help"))
async def help_bot(_, m: Message):
    await m.reply(
        f"Need help managing your group or channel? I can remove inactive members who haven't been seen for at least 5 days. Just add me as an admin and use the /kick_all command. Remember, I only kick inactive members, not ban them. They can always rejoin later if they become active again. For more information, check the bot's public repository: https://github.com/samuelmarc/kickallmembersbot")


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
                    await m.reply("❌ You are not an admin and cannot execute this command!")
                    return

            kick_count = 0
            last_seen_threshold = (datetime.now() - timedelta(days=5)).date()

            try:
                # Use get_chat_members with offsets and limits to iterate within API limitations
                offset = 0
                limit = 200
                while True:
                    members = await cl.get_chat_members(chat.id, offset=offset, limit=limit, filter="recent")
                    for member in members:
                        if member.user.id == cl.me.id:
                            continue
                        elif member.status == ChatMemberStatus.ADMINISTRATOR or member.status == ChatMemberStatus.OWNER:
                            continue

                        current_date = datetime.now().date()
                        last_seen_date = member.user.last_seen.date()
                        time_diff = (current_date - last_seen_date).days

                                              if time_diff >= 5:
                            try:
                                await chat.kick_member(member.user.id)
                                kick_count += 1
                            except FloodWait as e:
                                await asyncio.sleep(e.value)

                    offset += limit
                    if len(members) < limit:
                        break

            except Exception as e:
                logging.error(f"Error kicking members: {e}")
                await m.reply(f"❌ An error occurred while kicking members: {e}")

            if kick_count > 0:
                await m.reply(f"✅ Removed {kick_count} inactive members.")
            else:
                await m.reply(f"ℹ️ No inactive members found to remove.")

        else:
            await m.reply("❌ The bot needs administrator privileges with permission to manage chats and restrict members.")

    else:
        await m.reply("❌ The bot must be an admin to use this command.")


bot.run()
