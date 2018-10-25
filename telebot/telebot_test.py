import telebot

bot = telebot.TeleBot("676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA")

handler = 0
intro_mex = "Questo e' il bot del gruppo @scienza, \n\
/iscrivi iscriviti al database di utenti e a liste di interessi \n\
/modifica visiona e modifica la propria descrizione \n\
/liste consulta le attuali liste di interessi \n\
/nuovalista crea nuove liste"

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, intro_mex)

@bot.message_handler(commands=['iscrivi'])
def start_user_registration(message):
	global handler
	if not message.from_user.is_bot:
		bot.reply_to(message, "creazione nuovo record utente...")

		# Save this in database
		message.from_user.id
		message.from_user.username
		message.from_user.first_name
		message.from_user.last_name

		# this is to define step-by-step subscription
		handler = 1

		bot.reply_to(message, "dacci una breve presentazione di te (studio/lavoro, luogo ...)")

@bot.message_handler(func=lambda m: True if handler == 1 else False)
def first_registration(message):
	global handler
	if not message.from_user.is_bot:
		# if message.from_user.id is the same as before:
		# Save this in database as description
		message.text
		bot.reply_to(message,"A quali liste vuoi iscriverti?")
		# scrivere lista di liste
		handler = 2

@bot.message_handler(func=lambda m: True if handler == 2 else False)
def second_registration(message):
	global handler
	if not message.from_user.is_bot:
		# if message.from_user.id is the same as before:
		# Save this in database as subscriptions
		message.text
		bot.reply_to(message, "Grazie " + message.from_user.first_name)
		handler = 0


@bot.message_handler(func=lambda m: True if handler == 0 else False)
def reply_all(message):
	if not message.from_user.is_bot:
		bot.reply_to(message, "Ciao " + message.from_user.first_name + 
		                      ",\nusa /help o /start per una lista dei comandi")

bot.polling()
