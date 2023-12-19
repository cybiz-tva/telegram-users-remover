import telebot
import re
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Replace with your Telegram bot token
TOKEN = '5999713069:AAFYhnSI-79OCEEsnQL98K581QkUePq6T-8'

bot = telebot.TeleBot(TOKEN)

# Create an empty dictionary to store user responses
user_data = {}

# Replace with the path to your Google Sheets credentials JSON file
CREDENTIALS_JSON_PATH = 'D:/Downloads/mikfxdatabase-965088f7d3f9.json'

# URLs for images
WELCOME_IMAGE_URL = 'https://ibb.co/zXdD7M0'
SUCCESS_IMAGE_URL = 'https://ibb.co/m9C7h29'
INVALID_INPUT_IMAGE_URL = 'https://ibb.co/VHrqD1Y'
SUBMIT_EXNESS_ID_IMAGE_URL = 'https://ibb.co/ykbqh4n'
SUBMIT_MOBILE_NUMBER_IMAGE_URL = 'https://ibb.co/rvZYJ76'

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    user_data[user_id] = {}  # Initialize user data dictionary for the user

    # Get user details (name, username, user ID)
    name = message.from_user.first_name
    username = message.from_user.username
    user_data[user_id]['name'] = name
    user_data[user_id]['username'] = username
    user_data[user_id]['user_id'] = user_id

    # Send welcome message with image
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
        if re.match(r"^\d+$", message.text):  # Check if the input is digits only
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
        if re.match(r"^\d+$", message.text):  # Check if the input is digits only
            user_data[user_id]['exness_id'] = message.text

            # Save user data to Google Sheets
            save_user_data_to_google_sheets(user_data[user_id])

            bot.send_photo(chat_id, SUCCESS_IMAGE_URL, caption="Thank you! Your details have been submitted and saved.")
            user_data.pop(user_id)  # Remove user data from dictionary after submission
        else:
            send_invalid_input_message(chat_id)
            bot.register_next_step_handler(message, get_exness_id)

def send_invalid_input_message(chat_id):
    bot.send_photo(chat_id, INVALID_INPUT_IMAGE_URL, caption="Invalid input. Please submit the correct information.")
    bot.send_message(chat_id, "Please try again.")

def save_user_data_to_google_sheets(user_data):
    try:
        # Load credentials from the Google Sheets credentials JSON file
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        credentials = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_JSON_PATH, scope)
        gc = gspread.authorize(credentials)

        # Open the Google Sheets document by title
        spreadsheet = gc.open("Mikfx Database")

        # Select the first sheet
        sheet = spreadsheet.get_worksheet(0)

        # Get the next available row
        next_row = len(sheet.col_values(1)) + 1

        # Write data to Google Sheets
        sheet.update_cell(next_row, 1, str(datetime.now()))  # Date & time
        sheet.update_cell(next_row, 2, user_data['name'])  # Name
        sheet.update_cell(next_row, 3, user_data['username'])  # Username
        sheet.update_cell(next_row, 4, user_data['user_id'])  # User ID
        sheet.update_cell(next_row, 5, user_data['mobile_number'])  # Mobile number
        sheet.update_cell(next_row, 6, user_data['exness_id'])  # Exness ID

    except Exception as e:
        print(f"Error saving user data to Google Sheets: {e}")

if _name_ == "_main_":
    bot.polling(none_stop=True)
