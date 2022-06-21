import telebot
import os.path

from base64 import urlsafe_b64decode, urlsafe_b64encode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

TOKEN = "5259385883:AAFm-4DYkD8wEznwoSfyY9GLD9u5hdvrgg0"
CLIENT_FILE = "desktopClient.json"
# CLIENT_FILE_WEB = "client_secret_1268668511-7ohtd1abi7t4om9gg8mj8pb6vt5darl9.apps.googleusercontent.com.json"
GMAIL_REF = "https://mail.google.com/"
SCOPES = [GMAIL_REF]
service = False
bot = telebot.TeleBot(TOKEN)
def try_auth(userid):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    if not os.path.exists(f'database//{userid}//cacheEmails'):
        os.makedirs(f'database//{userid}//cacheEmails')

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(f'database//{userid}//token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(f'database//{userid}//token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        # results = service.users().labels().list(userId='me').execute()
        # labels = results.get('labels', [])
        return service

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')



def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"



def clean(text):
    return "".join(c if c.isalnum() else "_" for c in text)


def parse_parts(service, parts, folder_name, message):
    resultt = ""
    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")
            if part.get("parts"):
                parse_parts(service, part.get("parts"), folder_name, message)
            if mimeType == "text/plain":
                if data:
                    text = urlsafe_b64decode(data).decode()
                    resultt += text + "\n"
            elif mimeType == "text/html":
                if not filename:
                    filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                resultt += "Saving HTML to " + filepath + "\n" # Криво, конкат но пока для стабильности работы без f-строк
                with open(filepath, "wb") as f:
                    f.write(urlsafe_b64decode(data))
            else:
                for part_header in part_headers:
                    part_header_name = part_header.get("name")
                    part_header_value = part_header.get("value")
                    if part_header_name == "Content-Disposition":
                        if "attachment" in part_header_value:
                            resultt += "Saving the file: " + filename + "size: " + get_size_format(file_size) + "\n"
                            attachment_id = body.get("attachmentId")
                            attachment = service.users().messages() \
                                        .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                            data = attachment.get("data")
                            filepath = os.path.join(folder_name, filename)
                            if data:
                                with open(filepath, "wb") as f:
                                    f.write(urlsafe_b64decode(data))
    return resultt


def search_messages(service, query):
    result = service.users().messages().list(userId='me',q=query).execute()
    messages = [ ]
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me',q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages



def read_message(userid, service, message):
    res = ""
    msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    folder_name = "database//{userid}//email"
    has_subject = False
    if headers:
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == 'from':
                res += "From:" + value + "\n"
            if name.lower() == "to":
                res += "To:" + value + "\n"
            if name.lower() == "subject":
                has_subject = True
                folder_name = clean(value)
                folder_counter = 0
                while os.path.isdir(folder_name):
                    folder_counter += 1
                    if folder_name[-1].isdigit() and folder_name[-2] == "_":
                        folder_name = f"database//{userid}//{folder_name[:-2]}_{folder_counter}"
                    elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                        folder_name = f"database//{userid}//{folder_name[:-3]}_{folder_counter}"
                    else:
                        folder_name = f"database//{userid}//{folder_name}_{folder_counter}"
                os.mkdir("database//{userid}//" + folder_name)
                res += "Subject:" + value + "\n"
            if name.lower() == "date":
                res += "Date:" + value + "\n"
    if not has_subject:
        if not os.path.isdir(folder_name):
            os.mkdir("database//{userid}//" + folder_name)
    res = parse_parts(service, parts, "database//{userid}//" + folder_name, message) + "\n"
    res += "="*50 + "\n"
    return res




@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/auth":
        global service
        service = try_auth(message.from_user.id)
        bot.send_message(message.from_user.id, "Функция авторизации сработала, введите /find + ключевой текст или слово чтобы найти сообщение:")
    elif message.text == "/help":
        bot.send_message(message.from_user.id, "Напиши '/auth' для аутентификации")
    elif service and message.text[0:5] == "/find":
        results = search_messages(message.from_user.id, service, message.text[6:])
        for msg in results:
            print(msg)
            res = read_message(service, msg)
            bot.send_message(message.from_user.id, res)
    else:
        bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")


bot.polling(none_stop=True, interval=500)