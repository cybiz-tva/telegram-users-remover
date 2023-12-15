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
    chat_id = m.chat.id
    user_id = m.from_user.id
    print(f"Chat ID: {chat_id}, User ID: {user_id}")

    try:
        req_user_member = await chat.get_member(user_id)
    except Exception as e:
        await m.reply(f"❌ Error accessing member information: {e}")
        return

    if not req_user_member:
        await m.reply("❌ I cannot access your information. Ensure the bot has access to member details.")
        return

    if not req_user_member.privileges or not (req_user_member.privileges.can_manage_chat and req_user_member.privileges.can_restrict_members):
        await m.reply("❌ You are not authorized to use this command. Only admins with manage_chat and restrict_members permissions can do this.")
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


bot.run()
