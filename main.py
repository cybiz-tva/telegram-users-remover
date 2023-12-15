import asyncio
import logging
import os
from datetime import datetime, timedelta

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

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
            is_channel = True if m.chat.type == "channel" else False
            if not is_channel:
                req_user_member = await chat.get_member(m.from_user.id)
                if req_user_member is None or req_user_member.privileges is None:
                    await m.reply("❌ You are not admin and cannot execute this command!")
                    return

            # Send a message to the channel asking users to react within 1 minute
            message = await m.reply("React to this message within 1 minute to stay in the channel!")

            try:
                # Fetch the message again to get the up-to-date message object
                message = await cl.get_messages(m.chat.id, message.message_id)
                reactions = await message.await_reactions(timeout=60)
                for reaction in reactions:
                    user_id = reaction.from_user.id
                    await chat.unban_member(user_id)
                await m.reply(f"✅ Users who reacted within 1 minute have been kept.")
            except asyncio.TimeoutError:
                await m.reply("⚠️ Users who did not react within 1 minute have been removed.")

        else:
            await m.reply("❌ The bot is admin but does not have the necessary permissions!")
    else:
        await m.reply("❌ The bot must have admin!")


bot.run()
