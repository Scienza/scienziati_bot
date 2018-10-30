import telebot
import json
# import sqlite3

bot = telebot.TeleBot("676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA")

# database = sqlite3.connect("users.db", check_same_thread=False)
# sql_command = """
# CREATE TABLE user ( 
# id_number INTEGER PRIMARY KEY, 
# username VARCHAR(30), 
# first_name VARCHAR(20), 
# last_name VARCHAR(20),
# description VARCHAR(300));"""
# database.execute(sql_command)
with open('database.json', 'r') as f:  
	database = json.load(f)
with open('liste.json', 'r') as f:  
	liste = json.load(f)

intro_mex = """Questo e' il bot del gruppo @scienza,
/iscrivi iscriviti al database di utenti e a liste di interessi
/modifica visiona e modifica la propria descrizione
/liste consulta le attuali liste di interessi
/nuovalista crea nuove liste
/privs elenca i privilegi utente"""

privs_mex = """privs =-1 -> utente non registrato
       				 = 0 -> utente normale
       				 = 1 -> utente abituale
       				 = 2 -> utente assiduo
       				 = 3 -> utente storico (puo' inoltrare al canale, puo' creare nuove liste)
      				 = 4 -> amministratore
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
	global database
	if not message.from_user.is_bot:

		if database.get(str(message.from_user.id),None) is None:
			bot.reply_to(message, "creazione nuovo record utente...")

			# Save this in database
			database.update({str(message.from_user.id) : 
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

		msg = bot.reply_to(message, "dacci una breve presentazione di te (studio/lavoro, luogo ...)")

		# this is to define step-by-step subscription
		bot.register_next_step_handler(msg, first_registration)

def first_registration(message):
	global database
	global liste
	if not message.from_user.is_bot:
		# if message.from_user.id is the same as before save this in database as description
		database[str(message.from_user.id)]['description'] = message.text

		# sql_command = ("UPDATE users SET description =  "
		# + message.text 
		# + "WHEN id_number =" + str(message.from_user.id))
		# database.execute(sql_command)

		bot.reply_to(message,"A quali liste vuoi iscriverti?")
		msg = bot.reply_to(message,"seleziona fra: " + str(liste))
		# scrivere lista di liste
		bot.register_next_step_handler(msg, second_registration)

def second_registration(message):
	global database
	global liste
	if not message.from_user.is_bot:
		# if message.from_user.id is the same as before:
		# Save this in database as subscriptions
		msg = message.text.replace(',','')
		subscription = msg.split()
		database[str(message.from_user.id)]['liste'] = []
		for lista in subscription:
			if lista in liste:
				database[str(message.from_user.id)]['liste'].append(lista)
			else: 
				bot.reply_to(message, "Lista "+ lista + " non esistente")
		
		bot.reply_to(message, "Grazie " + message.from_user.first_name + "\n\
		ora sei iscritto a:\n " + str(database[str(message.from_user.id)]['liste']))
		with open('database.json', 'a') as f:  
			json.dump(database, f, indent=4)

### Fine Chat di iscrizione ###

@bot.message_handler(commands=['liste'])
def print_liste(message):
	global liste
	bot.reply_to(message, str(liste))

@bot.message_handler(commands=['nuovalista'])
def change_liste(message):
	global liste

	# set default for user not in database as privs = -1
	userprivs = database.get(str(message.from_user.id),{'privs' : -1})['privs']
	if userprivs > 2:
		nuovalista = message.text.split("nuovalista ",1)[-1]
		if "/nuovalista" in nuovalista:
			bot.reply_to(message, "specifica una lista dopo il comando /nuovalista.\nAd esempio /nuovalista fisica")
		elif nuovalista in liste:
			bot.reply_to(message, "lista gia' esistente")
		else:
			liste.append(nuovalista)
			bot.reply_to(message, "lista aggiunta\n"+str(liste))

	with open('liste.json', 'w') as f:  
		json.dump(liste, f, indent=4)


	# bot.reply_to(message, )

@bot.message_handler(commands=['database'])
def print_database(message):
	global database
	userprivs = database.get(str(message.from_user.id),{'privs' : -1})['privs']

	if userprivs > 2:
		bot.reply_to(message, str(database))
	else:
		bot.reply_to(message, str(database.get(message.from_user.id,None)))

@bot.message_handler(func=lambda m: True)
def reply_all(message):
	if not message.from_user.is_bot:
		bot.reply_to(message, "Ciao " + message.from_user.first_name + 
		                      ",\nusa /help o /start per una lista dei comandi")


bot.polling()
