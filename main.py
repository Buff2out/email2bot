import telebot
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN = "5259385883:AAFm-4DYkD8wEznwoSfyY9GLD9u5hdvrgg0"
CLIENT_FILE = "desktopClient.json"
CLIENT_FILE_WEB = "client_secret_1268668511-7ohtd1abi7t4om9gg8mj8pb6vt5darl9.apps.googleusercontent.com.json"
GMAIL_REF = "https://mail.google.com/"
SCOPES = [GMAIL_REF]
bot = telebot.TeleBot(TOKEN)
def try_auth():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        results = service.users().labels().list(userId='me').execute()
        labels = results.get('labels', [])

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')



def get_size_format(b, factor=1024, suffix="B"):
    pass



def clean(text):
    pass



@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/auth":
        service = try_auth()
        bot.send_message(message.from_user.id, "Функция авторизации сработала")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши '/auth' для аутентификации")
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")
        print("user sended")


bot.polling(none_stop=True, interval=0)