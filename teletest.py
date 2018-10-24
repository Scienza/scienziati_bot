import telepot
from pprint import pprint

bot = telepot.Bot('676490981:AAELlmTlQLD4_1HojhzWIX4yISDrVU5qDmA')
pprint(bot.getMe())

response = bot.getUpdates()
pprint(response)
