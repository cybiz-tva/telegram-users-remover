import logging
import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger("pyrogram").setLevel(logging.WARNING)

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
TARGET_EMOJI = "👍"

bot = Client(name="reactiontrackerbot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

logging.warning("⚡️ Bot Started!")

async def mark_user_engaged(chat_id, user_id):
    # Implement your logic for marking a user as engaged
    pass

async def check_inactive_user(chat_id, user_id):
    # Implement your logic for checking inactive users
    pass

@bot.on_message(filters.command("track_message"))
async def track_message_command(_, m):
    chat_id = m.chat.id
    tracked_message = await bot.send_message(
        chat_id,
        "React to this message to be considered engaged:",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(text=" Engage", callback_data="engaged"),
            InlineKeyboardButton(text="➖ Not interested", callback_data="not_interested"),
        ]]),
    )
    await bot.set_database(chat_id, {"tracked_message_id": tracked_message.message_id})

@bot.on_callback_query(filters.regex("^(engaged|not_interested)$"))
async def track_button_callback(_, cq):
    chat_id = cq.message.chat.id
    user_id = cq.from_user.id
    action = cq.data
    await cq.answer()
    if action == "engaged":
        await mark_user_engaged(chat_id, user_id)
    elif action == "not_interested":
        await cq.edit_message_text("Okay, you won't receive further engagement prompts.")
        # Consider adding confirmation or opting-out mechanism

async def main():
    while True:
        chat_id = bot.db.get("chat_id")  # Replace with your actual chat_id
        tracked_message_id = bot.db.get("tracked_message_id")
        
        if chat_id and tracked_message_id:
            try:
                message = await bot.get_messages(chat_id, message_ids=[tracked_message_id])
                for user_id, reaction in message.reactions.items():
                    if reaction == TARGET_EMOJI:
                        await mark_user_engaged(chat_id, user_id)
                    elif reaction in (None, "", TARGET_EMOJI + "-"):
                        await check_inactive_user(chat_id, user_id)
            except Exception as e:
                logging.error(f"Error processing reactions: {e}")

        await asyncio.sleep(60)  # Adjust polling interval as needed

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(bot.start())
    loop.create_task(main())
    loop.run_forever()
