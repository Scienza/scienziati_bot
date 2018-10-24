import telebot

bot = telebot.TeleBot("676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, "Howdy, how are you doing?")

@bot.message_handler(func=lambda m: True)
def echo_all(message):
	bot.reply_to(message, message.text)

bot.polling()
