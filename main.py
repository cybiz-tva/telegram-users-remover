import asyncio
import logging
import os
from datetime import datetime, timedelta

import uvloop
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import Message

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")

uvloop.install()

bot = Client(name="kickmemberbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.warning("⚡️ Bot Started!")


async def get_all_members(client, chat_id):
    all_members = []
    limit = 200  # Number of members per iteration

    while True:
        members_chunk = await client.iter_chat_members(chat_id, limit=limit)
        all_members.extend(members_chunk)

        if len(members_chunk) < limit:
            break

    return all_members


@bot.on_message(filters.command("kick_all") & (filters.channel | filters.group))
async def kick_all_members(cl: Client, m: Message):
    chat = await cl.get_chat(chat_id=m.chat.id)
    my = await chat.get_member(cl.me.id)

    if my.privileges and my.privileges.can_manage_chat and my.privileges.can_restrict_members:
        kick_count = 0
        all_members = await get_all_members(cl, chat.id)

        for member in all_members:
            if member.user.id != cl.me.id and \
               member.status not in [member.ADMINISTRATOR, member.OWNER]:
                join_date = member.joined_date
                if join_date and (datetime.now() - join_date) > timedelta(hours=2):
                    try:
                        await chat.kick_member(member.user.id, datetime.now() + timedelta(seconds=30))
                        kick_count += 1
                    except FloodWait as e:
                        await asyncio.sleep(e.value)

        await m.reply(f"✅ Total Users Removed: {kick_count}")

    else:
        await m.reply("❌ The bot must have admin with necessary permissions!")


bot.run()
