# Scienzabot di Prova

Two framework are currently under evaluation

### telepot

Suggested by Gabriele
[docs](https://telepot.readthedocs.io/en/latest/)
[github](https://github.com/nickoala/telepot)
`pip3 install telepot`

### telebot

Suggested by Vito. Seems more userfriendly.
[github](https://github.com/eternnoir/pyTelegramBotAPI)
`pip3 install pyTelegramBotAPI`

The first example: `telebot_test.py` does a simple echo of messages

## Todo
For a feature todo list:
[cf. bot team chat](https://github.com/orgs/Scienza/teams/bot)

I started implementing a little dialog using a global variable. This is not good enough if two or more users want to use the bot at the same time, find another solution but here's a canvas.

More stuff to do:

- give a /start, /help more informative message (Italian)
- estract userID and other features to be saved from the message queue into a python structure
- save dictionary database to file, and eventually to SQL structured database
- verify that subscription message to taglists is included in the list "liste". Split and organize as list

I (Andrea) suggest to use telebot and work from the provided example. It seems more intuitive for everybody even though telepot is more low level.
