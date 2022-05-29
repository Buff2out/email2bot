import telebot

TOKEN = "5259385883:AAFm-4DYkD8wEznwoSfyY9GLD9u5hdvrgg0"

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