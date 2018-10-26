import telebot
# import sqlite3

bot = telebot.TeleBot("676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA")

handler = 0
# database = sqlite3.connect("users.db", check_same_thread=False)
# sql_command = """
# CREATE TABLE user ( 
# id_number INTEGER PRIMARY KEY, 
# username VARCHAR(30), 
# first_name VARCHAR(20), 
# last_name VARCHAR(20),
# description VARCHAR(300));"""
# database.execute(sql_command)
database = {}
liste = ['fisica', 'matematica', 'informatica']

intro_mex = """Questo e' il bot del gruppo @scienza, \n
/iscrivi iscriviti al database di utenti e a liste di interessi \n
/modifica visiona e modifica la propria descrizione \n
/liste consulta le attuali liste di interessi \n
/nuovalista crea nuove liste\n
/privs elenca i privilegi utente"""

privs_mex = """privs =-1 -> utente non registrato\n
       				 = 0 -> utente normale\n
       				 = 1 -> utente abituale\n
       				 = 2 -> utente assiduo\n
       				 = 3 -> utente storico (puo' inoltrare al canale, puo' creare nuove liste)\n
      				 = 4 -> amministratore\n
		       		 = 5 -> fondatore"""

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, intro_mex)

@bot.message_handler(commands=['privs'])
def send_privs(message):
	bot.reply_to(message, privs_mex)

### Chat di Iscrizione ###
@bot.message_handler(commands=['iscrivi'])
def start_user_registration(message):
	global handler
	global database
	if not message.from_user.is_bot:
		bot.reply_to(message, "creazione nuovo record utente...")

		# Save this in database
		database.update({message.from_user.id : 
			{'username' : str(message.from_user.username),
			'first_name': str(message.from_user.first_name),
			'last_name' : str(message.from_user.last_name),
			'privs' : 0,
			'description': '',
			'liste': ''
			} 
		})

		# sql_command = ("INSERT INTO user (id_number, username, first_name, last_name)\
    	# VALUES ("
		# + str(message.from_user.id) + ", "
		# + str(message.from_user.username) + ", " 
		# + str(message.from_user.first_name) + ", "
		# + str(message.from_user.last_name) + ");")
		# database.execute(sql_command)

		# this is to define step-by-step subscription
		handler = 1

		bot.reply_to(message, "dacci una breve presentazione di te (studio/lavoro, luogo ...)")

@bot.message_handler(func=lambda m: True if handler == 1 else False)
def first_registration(message):
	global handler
	global database
	global liste
	if not message.from_user.is_bot:
		# if message.from_user.id is the same as before save this in database as description
		database[message.from_user.id]['description'] = message.text

		# sql_command = ("UPDATE users SET description =  "
		# + message.text 
		# + "WHEN id_number =" + str(message.from_user.id))
		# database.execute(sql_command)

		bot.reply_to(message,"A quali liste vuoi iscriverti?")
		bot.reply_to(message,"seleziona fra: " + str(liste))
		# scrivere lista di liste
		handler = 2

@bot.message_handler(func=lambda m: True if handler == 2 else False)
def second_registration(message):
	global handler
	global database
	global liste
	if not message.from_user.is_bot:
		# if message.from_user.id is the same as before:
		# Save this in database as subscriptions
		database[message.from_user.id]['liste'] = message.text
		bot.reply_to(message, "Grazie " + message.from_user.first_name)
		handler = 0

### Fine Chat di iscrizione ###

@bot.message_handler(commands=['liste'])
def print_liste(message):
	global liste
	bot.reply_to(message, str(liste))

@bot.message_handler(commands=['nuovalista'])
def change_liste(message):
	global liste

	# set default for user not in database as privs = -1
	userprivs = database.get(message.from_user.id,{'privs' : -1})['privs']
	if userprivs > 2:
		nuovalista = message.text.split("nuovalista ",1)[-1]
		if "/nuovalista" in nuovalista:
			bot.reply_to(message, "specifica una lista dopo il comando /nuovalista.\nAd esempio /nuovalista fisica")
		elif nuovalista in liste:
			bot.reply_to(message, "lista gia' esistente")
		else:
			liste.append(nuovalista)
			bot.reply_to(message, "lista aggiunta\n"+str(liste))

	# bot.reply_to(message, )

@bot.message_handler(commands=['database'])
def print_database(message):
	global database
	userprivs = database.get(message.from_user.id,{'privs' : -1})['privs']
	if userprivs > 2:
		bot.reply_to(message, str(database))
	else:
		bot.reply_to(message, str(database.get(message.from_user.id,None)))


@bot.message_handler(func=lambda m: True if handler == 0 else False)
def reply_all(message):
	if not message.from_user.is_bot:
		bot.reply_to(message, "Ciao " + message.from_user.first_name + 
		                      ",\nusa /help o /start per una lista dei comandi")


bot.polling()
