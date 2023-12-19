import os
import telebot
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Get sensitive information from environment variables
TOKEN = os.environ.get('5999713069:AAFYhnSI-79OCEEsnQL98K581QkUePq6T-8')
CREDENTIALS_JSON_PATH = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH')

bot = telebot.TeleBot(TOKEN)

user_data = {}

WELCOME_IMAGE_URL = 'https://ibb.co/zXdD7M0'
SUCCESS_IMAGE_URL = 'https://ibb.co/m9C7h29'
INVALID_INPUT_IMAGE_URL = 'https://ibb.co/VHrqD1Y'
SUBMIT_EXNESS_ID_IMAGE_URL = 'https://ibb.co/ykbqh4n'
SUBMIT_MOBILE_NUMBER_IMAGE_URL = 'https://ibb.co/rvZYJ76'

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_data[user_id] = {}

    name = message.from_user.first_name
    username = message.from_user.username
    user_data[user_id]['name'] = name
    user_data[user_id]['username'] = username
    user_data[user_id]['user_id'] = user_id

    bot.send_photo(user_id, WELCOME_IMAGE_URL, caption=f"Welcome, {name}! Click on the button to submit your details:",
                   reply_markup=create_submit_button())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id

    if call.data == "submit_button":
        bot.send_photo(chat_id, SUBMIT_MOBILE_NUMBER_IMAGE_URL, caption="Submit your mobile number (digits only):")
        bot.register_next_step_handler(call.message, get_mobile_number)

    elif call.data == "submit_exness_id_button":
        bot.send_photo(chat_id, SUBMIT_EXNESS_ID_IMAGE_URL, caption="Submit your Exness ID (digits only):")
        bot.register_next_step_handler(call.message, get_exness_id)

def create_submit_button():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_submit = telebot.types.InlineKeyboardButton("Submit", callback_data="submit_button")
    markup.add(button_submit)
    return markup

def get_mobile_number(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if 'mobile_number' not in user_data[user_id]:
        if re.match(r"^\d+$", message.text):
            user_data[user_id]['mobile_number'] = message.text
            bot.send_photo(chat_id, SUBMIT_EXNESS_ID_IMAGE_URL, caption="Submit your Exness ID (digits only):",
                           reply_markup=create_submit_exness_id_button())
            bot.register_next_step_handler(message, get_exness_id)
        else:
            send_invalid_input_message(chat_id)
            bot.register_next_step_handler(message, get_mobile_number)

def create_submit_exness_id_button():
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    button_submit_exness_id = telebot.types.InlineKeyboardButton("Submit Exness ID", callback_data="submit_exness_id_button")
    markup.add(button_submit_exness_id)
    return markup

def get_exness_id(message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if 'exness_id' not in user_data[user_id]:
        if re.match(r"^\d+$", message.text):
            user_data[user_id]['exness_id'] = message.text
            save_user_data_to_google_sheets(user_data[user_id])
            bot.send_photo(chat_id, SUCCESS_IMAGE_URL, caption="Thank you! Your details have been submitted and saved.")
            user_data.pop(user_id)
        else:
            send_invalid_input_message(chat_id)
            bot.register_next_step_handler(message, get_exness_id)

def send_invalid_input_message(chat_id):
    bot.send_photo(chat_id, INVALID_INPUT_IMAGE_URL, caption="Invalid input. Please submit the correct information.")
    bot.send_message(chat_id, "Please try again.")

def save_user_data_to_google_sheets(user_data):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_JSON_PATH, scope)
        gc = gspread.authorize(credentials)

        spreadsheet = gc.open("Mikfx Database")
        sheet = spreadsheet.get_worksheet(0)

        next_row = len(sheet.col_values(1)) + 1

        sheet.update_cell(next_row, 1, str(datetime.now()))
        sheet.update_cell(next_row, 2, user_data['name'])
        sheet.update_cell(next_row, 3, user_data['username'])
        sheet.update_cell(next_row, 4, user_data['user_id'])
        sheet.update_cell(next_row, 5, user_data['mobile_number'])
        sheet.update_cell(next_row, 6, user_data['exness_id'])

    except Exception as e:
        print(f"Error saving user data to Google Sheets: {e}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
