import telebot
#pip3 install PyTelegramBotAPI
# import json
import sqlite3

###
## Bot Inizialization
###

#Create the bot instance
bot = telebot.TeleBot("676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA")
botInfo = bot.get_me()
print("Authorized on @" + botInfo.username)


###
## Database Inizialization
###

#Initialize the database connection 
dbConnection = sqlite3.connect('database.sqlitedb', check_same_thread=False)

#Set the resulting array to be associative
# https://stackoverflow.com/a/2526294
dbConnection.row_factory = sqlite3.Row

#Sets the database cursor.
#It is used to submit queires to the DB and manage it
# https://docs.python.org/2/library/sqlite3.html
dbC = dbConnection.cursor()
# Remember to close the connection at the end of the program with conn.close()

#This part of the code is used to initalize the database.
#It runs the "seed" query
#This is the query that is used to initialize the SQLite3 database
initQuery= """CREATE TABLE IF NOT EXISTS `Users` (
`ID`  INTEGER NOT NULL UNIQUE,
`Nickname`  TEXT NOT NULL,
`Biography`  TEXT,
`Status`  INTEGER NOT NULL DEFAULT 0,
`Permissions`  INTEGER DEFAULT 0,
`ITMessageNumber`  INTEGER DEFAULT 0,
`OTMessageNumber`  INTEGER DEFAULT 0,
`LastSeen`  TEXT DEFAULT '0000-00-00 00:00:00',
PRIMARY KEY(`ID`)
);

CREATE TABLE IF NOT EXISTS `Lists` (
`ID`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
`Name`  TEXT NOT NULL UNIQUE,
`Desc`  TEXT
);

CREATE TABLE IF NOT EXISTS `Subscriptions` (
`ID`  INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
`List`  INTEGER NOT NULL,
`User`  INTEGER NOT NULL,
FOREIGN KEY(`User`) REFERENCES `Users`(`ID`),
FOREIGN KEY(`List`) REFERENCES `Lists`(`ID`)
);"""
# Seeds the databse - Executes the inital query
#I use executescript instead of excut to permit to do multiple queries
dbC.executescript(initQuery)
# Save (commit) the changes
dbConnection.commit()



###
# Constant message values
###

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

# Status legend
# -2 - Waiting for biograhy
# -1 - User just created - needs to insert bio
# 0 - User created
# 15 - Banned
#
#


# Permissions legend
#
# xxx0 - Admin flag - 1 = admin
# xx0x - Channed flag - 1 = can post to channel
# x0xx -  flag - 1 = can post to channel
#

###
# Bot functions
###

#Start command.
# This is the function called when the bot is started or the help commands are sent
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, intro_mex)
	bot.reply_to(message, "Tost")

# Replies with the static message before
@bot.message_handler(commands=['privs'])
def send_privs(message):
	bot.reply_to(message, privs_mex)

### Messaggio di Iscrizione 
@bot.message_handler(commands=['iscrivi'])
def start_user_registration(message):
	bot.reply_to(message, "Test")
	if not message.from_user.is_bot and message.text != "" :
		# Tries to see 
		dbC = dbConnection.cursor()
		dbC.execute('SELECT * FROM Users WHERE ID=?', (message.from_user.id,))
		rows = dbC.fetchall()

		#if database.get(str(message.from_user.id),None) is None:
		if len(rows) > 0:
			#The user exists in database
			bot.reply_to(message, "Sei già registrato in database. se desideri modificare la tua biografia puoi farlo mediante il comando /bio")
		else:
			#The user needs to be created
			bot.reply_to(message, "creazione nuovo record utente...")
			#Insert 
			dbC = dbConnection.cursor()
			res = dbC.execute('INSERT INTO Users (ID, Nickname, Status) VALUES (?,?,?)', (message.from_user.id, message.from_user.username, -1,) )
			dbConnection.commit()
			if res:
				msg = bot.reply_to(message, "Congratulazioni, ti sei registrato correttamente! Ora puoi procedere ad inserire la tua biografia attraverso il comando /bio")
			else:
				msg = bot.reply_to(message, "Errore nella creazione del record")


		# this is to define step-by-step subscription
		#bot.register_next_step_handler(msg, first_registration)




### Aggioramento/ impostaizone bio
@bot.message_handler(commands=['bio'])
def setBio(message):
	if not message.from_user.is_bot and message.text != "" :
		# Gets info about the user
		dbC = dbConnection.cursor()
		dbC.execute('SELECT * FROM Users WHERE ID=?', (message.from_user.id,))
		rows = dbC.fetchall()

		#Check if the user exists
		if len(rows) < 1:
			#the user does not exist
			msg = bot.reply_to(message, "Non sei ancora registrato. Puoi registrarti attraverso il comando /iscrivi ")

		#Check its status
		if len(rows) == 1:
			#There's only one user, as it's supposed to be
			#Check if the user needs to set a biography
			if rows[0]["Status"] == -1:
				#Asks for the bio
				dbC = dbConnection.cursor()
				res = dbC.execute('UPDATE Users SET Status=? WHERE ID = ?;', (-2 , message.from_user.id,) )
				#res = dbC.execute('UPDATE Users SET Status=?, Biography=? WHERE employeeid = ?;', (0, message.text, message.from_user.id,) )
				#Tries to force the user to reply to the message
				markup = telebot.types.ForceReply(selective=False)
				msg = bot.reply_to(message, "Per impostare una biografia, scrivila in chat privata o rispondendomi", reply_markup=markup)
				dbConnection.commit()
			else:
				#Nothing to do here
				msg = bot.reply_to(message, "You are already ok")

		else:
			#Something's wrongs, there shouldn't be more than one 1 user with the same ID
			#The "error code" is a random string, univoque in the code, to see where the code faulted
			msg = bot.reply_to(message, "Errore generico, conttattare un admin.\nCodice: #E643")



@bot.message_handler(func=lambda m: True)
def genericMessageHandler(message):
	#get info about the user
	dbC = dbConnection.cursor()
	dbC.execute('SELECT * FROM Users WHERE ID=?', (message.from_user.id,))
	rows = dbC.fetchall()


	print(rows)
	#Check for biography
	if len(rows) == 1:
		if rows[0]["Status"] == -2:
			#User is setting the Bio
			if message.chat.type == "private":
				dbC = dbConnection.cursor()
				res = dbC.execute('UPDATE Users SET Status=?, Biography=? WHERE ID = ?;', (0, message.text, message.from_user.id,) )
				msg = bot.reply_to(message, "Biografia impostata con successo!")
				#Tries to force the user to reply to the message
				
			#TODO: Not sure about the order - needs to be checked
			elif message.chat.type == "group" or message.chat.type == "supergroup" and message.chat.reply_to_message == botInfo.ID:
				dbC = dbConnection.cursor()
				res = dbC.execute('UPDATE Users SET Status=?, Biography=? WHERE ID = ?;', (0, message.text, message.from_user.id,) )
				msg = bot.reply_to(message, "Biografia impostata con successo!")
		dbConnection.commit()





"""
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
"""
### Fine Chat di iscrizione ###


###
# Bot hooks
###
"""
@bot.message_handler(commands=['liste'])
def print_liste(message):
	global liste
	bot.reply_to(message, str(liste))
""" 

"""
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
"""


"""
@bot.message_handler(commands=['database'])
def print_database(message):
	global database
	userprivs = database.get(str(message.from_user.id),{'privs' : -1})['privs']

	if userprivs > 2:
		bot.reply_to(message, str(database))
	else:
		bot.reply_to(message, str(database.get(message.from_user.id,None)))
"""

@bot.message_handler(func=lambda m: True)
def reply_all(message):
	if not message.from_user.is_bot:
		bot.reply_to(message, "Ciao " + message.from_user.first_name + 
		                      ",\nusa /help o /start per una lista dei comandi")


###
#Starts the bot
###

bot.polling()
