import telebot
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN = "5259385883:AAFm-4DYkD8wEznwoSfyY9GLD9u5hdvrgg0"
CLIENT_FILE = "client_secret_1268668511-7ohtd1abi7t4om9gg8mj8pb6vt5darl9.apps.googleusercontent.com.json"
gmailRef = "https://mail.google.com/"
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "Привет":
        bot.send_message(message.from_user.id, "Привет, чем я могу тебе помочь?")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши 'Привет'")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
        print("user sended")

bot.polling(none_stop=True, interval=0)