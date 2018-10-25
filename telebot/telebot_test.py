import telebot

bot = telebot.TeleBot("676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA")

intro_mex = "Questo e' il bot del gruppo @scienza, \niscrivi al database e a liste di interessi"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, intro_mex)

@bot.message_handler(commands=['nuovo'])
def registra(message):
	bot.reply_to(message, "crea nuovo utente")

@bot.message_handler(func=lambda m: True)
def reply_all(message):
	if not message.from_user.is_bot:
		bot.reply_to(message, "Ciao " + message.from_user.first_name + ",\nusa /help o /start per una lista dei comandi")

bot.polling()
