import logging
import os
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime, timedelta
import asyncio

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

bot = Client(name="kickmemberbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.warning("⚡️ Bot Started!")

@bot.on_message(filters.command("remove") & (filters.channel | filters.group))
async def remove_members(cl: Client, m: Message):
    chat = await cl.get_chat(chat_id=m.chat.id)
    my = await chat.get_member(cl.me.id)
    if my.status in ["administrator", "creator"]:
        is_channel = m.chat.type == "channel"
        if not is_channel:
            req_user_member = await chat.get_member(m.from_user.id)
            if req_user_member.status not in ["administrator", "creator"]:
                await m.reply("❌ You are not an admin and cannot execute this command!")
                return

        user_ids = m.text.split()[1:]
        if not user_ids:
            await m.reply("❌ Please provide user IDs to remove.")
            return

        kick_count = 0
        for user_id in user_ids:
            try:
                resp = await kick_chat_member(chat.id, int(user_id))
                if resp and resp.ok:
                    kick_count += 1
                else:
                    await m.reply(f"❌ Failed to remove user with ID {user_id}.")
            except Exception as e:
                await m.reply(f"❌ Failed to remove user with ID {user_id}: {str(e)}")

        await m.reply(f"✅ Total Users Removed: {kick_count}")
    else:
        await m.reply("❌ The bot is not an admin or does not have the necessary permissions!")

async def kick_chat_member(chat_id, user_id):
    # PipedreamHQ library method implementation
    try:
        resp = await bot.telegram_bot_api.kick_chat_member(chat_id, user_id)
        return resp
    except Exception as e:
        raise e

bot.run()
