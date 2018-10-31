import telebot
#pip3 install PyTelegramBotAPI
import time
import sqlite3

#Settings class

class Settings:
	TelegramApiKey = "676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA"
	SupremeAdmins = []
	ITGroup = 0
	OTGroup = -1001176680738


###
## Bot Inizialization
###

#Create the bot instance
bot = telebot.TeleBot(Settings.TelegramApiKey)
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

class constResources:

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
	
	gdpr_message = "Raccogliamo il numero di messaggi, nickname, ID e ultima volta che l'utente ha scritto. Per richiedere l'eliminazione dei propri dati contattare un amministratore ed uscire dal gruppo"



###
# Constant values
#  Those values are static and are used to represent the user's state/permission
#  The Permission funtion are used to execute bitwise operations, and the status are simply used to compare the statuses
###

# Status legend
# -2 - Waiting for biograhy
# -1 - User just created - needs to insert bio
# 0 - User created
# 15 - Banned


class UserStatus: #Enum emulator
	WAITING_FOR_BIOGRAPHY = -2
	USER_JUST_CREATED = -1
	ACTIVE = 0
	BANNED = 15

	#Dummy functions - Those functions are "dummy": they are just used to compare a given input to the value in the class
	def IsWaitingForFirstBio(status):
		if status == UserStatus.WAITING_FOR_FIRST_BIOGRAPHY:
			return True
		return False

	def IsWaitingForBio(status):
		if status == UserStatus.WAITING_FOR_BIOGRAPHY:
			return True
		return False

	def IsJustCreated(status):
		if status == UserStatus.USER_JUST_CREATED:
			return True
		return False

	def IsActive(status):
		if status == UserStatus.ACTIVE:
			return True
		return False

	def IsBanned(status):
		if status == UserStatus.BANNED:
			return True
		return False

	# Complex functions
	#CanEnterBio Is used whern checking if a user has privileges to edit its Biography
	def CanEnterBio(status):
		if status == UserStatus.BANNED:
			return False 
		return True



# Permissions legend
#
# xxx0 - Admin flag - 1 = admin
# xx0x - Channed flag - 1 = can post to channel
# x0xx -  flag - 1 = can post to channel
#
class UserPermission: #Siply do an AND with the permission
	ADMIN=int('1', 2)
	CHANNEL=int('10', 2)
	CREATE_LIST=int('100', 2)

	def IsAdmin(permission):
		if (permission & UserPermission.ADMIN) == UserPermission.ADMIN:
			return True
		return False
	
	def CanForwardToChannel(permission):
		if (permission & UserPermission.CHANNEL) == UserPermission.CHANNEL:
			return True
		return False
	
	def CanCreateList(permission):
		if (permission & UserPermission.CREATE_LIST) == UserPermission.CREATE_LIST:
			return True
		return False






###
# Helper functions
#  Those functions will be used as support functions for the bot. 
#  Those are mosltry "database wrappers"
###

#GetUser is used to return the row corresponding to the user in the database.
#It went introduced because the same query repeted over and over
def GetUser(userID):
		#Create a database cursor
	dbC = dbConnection.cursor()
	#Selects the users
	dbC.execute('SELECT * FROM Users WHERE ID=?', (userID,))
	#Fetch the results
	rows = dbC.fetchall()
	#Check if the users exists
	if len(rows) > 0:
		if len(rows) > 1:
			#something's wrong here, the ID shouln't be greater than one
			raise Exception('The user exceed 1. Something could be wrong with the database. Code error #S658')
		else:
			#The users exists, returns the permission
			return rows[0]
	else:
		#No record found - ID could be erroneous
		#TODO: Throw error?
		return False

#UpdateBio is a helper function to update the biography of a user.
#It returns true in case of success, otherwise it returns false
def UpdateBio(userdID, bio):
	dbC = dbConnection.cursor()
	res = dbC.execute('INSERT INTO Users (ID, Nickname, Status) VALUES (?,?,?)', (userdID, bio, UserStatus.USER_JUST_CREATED,) )
	if res:
		CommitDb()
		return True
	return False

# GetUserPermissionsValue takes the userID as input and returns the permission value (int) direclty from the database
def GetUserPermissionsValue(userID):
	user = GetUser(userID)
	if user != False:
		return user["Permissions"]
	#No user exist, returning Flase for now
	return False

def GetUserStatusValue(userID):
	user = GetUser(userID)
	if user != False:
		return user["Status"]
	#No user exist, returning Flase for now
	return False

#IncrITGroupMessagesCount increments the number of messages in the IT group
def IncrITGroupMessagesCount(userID):
	dbC = dbConnection.cursor()
	res = dbC.execute('UPDATE Users SET ITMessageNumber = ITMessageNumber + 1 WHERE ID = ?', (userID,) )
	if res:
		CommitDb()
		return True
	return False

#IncrOTGroupMessagesCount increments the number of messages in the OT group
def IncrOTGroupMessagesCount(userID):
	dbC = dbConnection.cursor()
	res = dbC.execute('UPDATE Users SET OTMessageNumber = OTMessageNumber + 1 WHERE ID = ?', (userID,) )
	if res:
		CommitDb()
		return True
	return False

def UpdateLastSeen(userID, date):
	dbC = dbConnection.cursor()
	res = dbC.execute('UPDATE Users SET LastSeen=? WHERE ID = ?', (date, userID,) )
	if res:
		CommitDb()
		return True
	return False

def CommitDb():
	dbConnection.commit()


#CreateNewListWithoutDesc creates a new list without a description 
def CreateNewListWithoutDesc(name):
	CreateNewList(name, "")


#CreateNewListWithoutDesc creates a new list 
def CreateNewList(name, desc):
	dbC = dbConnection.cursor()
	res = dbC.execute('INSERT INTO Lists (Name, Desc) VALUES (?,?)', (name, desc,) )
	if res:
		return True
	return False

#Abort the inserting process of a new Bio
#WARNING: CHECK IF USER IS BANNED BEFORE, OR HE WILL GET UNBANNED
def abortNewBio(userID):
	dbC = dbConnection.cursor()
	res = dbC.execute('UPDATE Users SET Status=? WHERE ID = ?', (UserStatus.ACTIVE, userID,) )
	if res:
		CommitDb()
		return True
	return False

###
# Bot functions
###

#Start command.
# This is the function called when the bot is started or the help commands are sent
@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	bot.reply_to(message, constResources.intro_mex)
	bot.reply_to(message, "Tost")

# Replies with the static message before
@bot.message_handler(commands=['privs'])
def send_privs(message):
	bot.reply_to(message, constResources.privs_mex)

# Replies with the static message before
@bot.message_handler(commands=['gdpr'])
def send_gdrp(message):
	bot.reply_to(message, constResources.gdpr_message)

### Messaggio di Iscrizione 
@bot.message_handler(commands=['iscrivi'])
def start_user_registration(message):
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
			res = dbC.execute('INSERT INTO Users (ID, Nickname, Status) VALUES (?,?,?)', (message.from_user.id, message.from_user.username, UserStatus.USER_JUST_CREATED,) )
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
		user = GetUser(message.from_user.id)
		#Check if the user exists
		if user == False:
			#the user does not exist
			msg = bot.reply_to(message, "Non sei ancora registrato. Puoi registrarti attraverso il comando /iscrivi ")
		#Check its status
		else:
			#There's only one user, as it's supposed to be
			#Check if the user needs to set a biography
			if UserStatus.CanEnterBio(user["Status"]):
				#Asks for the bio
				dbC = dbConnection.cursor()
				res = dbC.execute('UPDATE Users SET Status=? WHERE ID = ?;', (UserStatus.WAITING_FOR_BIOGRAPHY , message.from_user.id,) )
				#res = dbC.execute('UPDATE Users SET Status=?, Biography=? WHERE employeeid = ?;', (0, message.text, message.from_user.id,) )
				#Tries to force the user to reply to the message
				#markup = telebot.types.ForceReply(selective=False)
				markup = telebot.types.InlineKeyboardMarkup()
				markup.row_width = 2
				markup.add(telebot.types.InlineKeyboardButton('❌ Annulla', callback_data=f"aBio"))
				msg = bot.reply_to(message, "Per impostare una biografia, scrivila in chat privata o rispondendomi", reply_markup=markup)
				dbConnection.commit()
			else:
				#Nothing to do here
				msg = bot.reply_to(message, "You are already ok")


#Creazione di una nuova lista
@bot.message_handler(commands=['newlist', 'nuovalista'])
def newList(message):
	if UserPermission.CanCreateList(GetUserPermissionsValue(message.from_user.id)):
		values = message.test.split(' ')

	else:
		msg = bot.reply_to(message, "Error 403 - Unauthorized")

#Lista delle liste
@bot.message_handler(commands=['lists', 'liste'])
def showLists(message):
	#getLists()#TODO implement method
	bot.reply_to(message, "NOT IMPLEMENTED EXCEPTION! \n AUTODESTRUCTION SEQUENCE CORRECTLY STARTED")

@bot.message_handler(func=lambda m: True)
def genericMessageHandler(message):
	#get info about the user

	user = GetUser(message.from_user.id)
	if user != False:
		#The user is registred in DB

		#Check for biography
		if user["Status"] == UserStatus.WAITING_FOR_BIOGRAPHY:
			#User is setting the Bio
			if message.chat.type == "private":
				dbC = dbConnection.cursor()
				res = dbC.execute('UPDATE Users SET Status=?, Biography=? WHERE ID = ?', (UserStatus.ACTIVE, message.text, message.from_user.id,) )
				msg = bot.reply_to(message, "Biografia impostata con successo!")
				#Tries to force the user to reply to the message
				
			#TODO: Not sure about the order - needs to be checked
			elif message.chat.type == "group" or message.chat.type == "supergroup" and message.reply_to_message != None and message.reply_to_message.from_user.id == botInfo.id:
				dbC = dbConnection.cursor()
				res = dbC.execute('UPDATE Users SET Status=?, Biography=? WHERE ID = ?', (UserStatus.ACTIVE, message.text, message.from_user.id,) )
				msg = bot.reply_to(message, "Biografia impostata con successo!")
		else:
			#Normal message, increment message counter
			#update lastseen
			UpdateLastSeen(message.from_user.id, time.strftime('%Y-%m-%d %H:%M:%S',
			#Telegram sends the date in a epoch format 
			#https://core.telegram.org/bots/api#message
			# Need to convert it
			#https://stackoverflow.com/a/12400584
			time.localtime(message.date)))

			if not message.from_user.is_bot and message.text != "" :
				if message.chat.id == Settings.ITGroup:
					#Increment IT group messages cunt
					IncrITGroupMessagesCount(message.from_user.id)
				elif message.chat.id == Settings.OTGroup:
					#Increment OT group messages cunt
					IncrOTGroupMessagesCount(message.from_user.id)
		dbConnection.commit()




@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
	#Sample response
	# {'game_short_name': None, 'chat_instance': '5537587246343980605', 'id': '60524995438318427', 'from_user': {'id': 14092073, 'is_bot': False, 'first_name': 'Pandry', 'username': 'Pandry', 'last_name': None, 'language_code': 'en-US'}, 'message': {'content_type': 'text', 'message_id': 2910, 'from_user': <telebot.types.User object at 0x040BBB30>, 'date': 1541000520, 'chat': <telebot.types.Chat object at 0x040BBB10>, 'forward_from_chat': None, 'forward_from': None, 'forward_date': None, 'reply_to_message': <telebot.types.Message object at 0x040BBFB0>, 'edit_date': None, 'media_group_id': None, 'author_signature': None, 'text': 'Per impostare una biografia, scrivila in chat privata o rispondendomi', 'entities': None, 'caption_entities': None, 'audio': None, 'document': None, 'photo': None, 'sticker': None, 'video': None, 'video_note': None, 'voice': None, 'caption': None, 'contact': None, 'location': None, 'venue': None, 'new_chat_member': None, 'new_chat_members': None, 'left_chat_member': None, 'new_chat_title': None, 'new_chat_photo': None, 'delete_chat_photo': None, 'group_chat_created': None, 'supergroup_chat_created': None, 'channel_chat_created': None, 'migrate_to_chat_id': None, 'migrate_from_chat_id': None, 'pinned_message': None, 'invoice': None, 'successful_payment': None, 'connected_website': None, 'json': {'message_id': 2910, 'from': {'id': 676490981, 'is_bot': True, 'first_name': 'ScienzaBot', 'username': 'scienzati_bot'}, 'chat': {'id': -1001176680738, 'title': '@Scienza World Domination', 'type': 'supergroup'}, 'date': 1541000520, 'reply_to_message': {'message_id': 2909, 'from': {'id': 14092073,
	# 'is_bot': False, 'first_name': 'Pandry', 'username': 'Pandry', 'language_code': 'en-US'}, 'chat': {'id': -1001176680738, 'title': '@Scienza World Domination', 'type': 'supergroup'}, 'date': 1541000520, 'text': '/bio', 'entities': [{'offset': 0, 'length': 4, 'type': 'bot_command'}]}, 'text': 'Per impostare una biografia, scrivila in chat privata o rispondendomi'}}, 'data': 'annulla', 'inline_message_id': None}
	#
	user = GetUser(call.from_user.id)
	if user != False:
		#Check if is to abort bio
		if call.data == "aBio":
			#Check if the guy who pressed is the same who asked to set the bio
			if call.from_user.id == call.message.reply_to_message.from_user.id:
				#Check that the user needs to set the bio
				if user["Status"] == UserStatus.WAITING_FOR_BIOGRAPHY :
					success = abortNewBio(call.from_user.id)
					if success:
						markup = telebot.types.InlineKeyboardMarkup()
						bot.edit_message_text("Annullato." , call.message.chat.id , call.message.message_id, call.id, reply_markup=markup)
				else:
					bot.delete_message(call.message.chat.id , call.message.message_id)
						
	#else:
	#	Who are you?


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
"""
@bot.message_handler(func=lambda m: True)
def reply_all(message):
	if not message.from_user.is_bot:
		bot.reply_to(message, "Ciao " + message.from_user.first_name + 
		                      ",\nusa /help o /start per una lista dei comandi")
"""

###
#Starts the bot
###

bot.polling()
