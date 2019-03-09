import configparser
from ast import literal_eval

config=configparser.ConfigParser()
modules={'main':False,'reload':False}
bot=False
connected=False
datafolder='data/'

dhelp={'kahoot':
	   "`k!kahoot [time]`: Start a game, time controls how many seconds people have to join.",
	   'help':
	   "`k!help [command]`: Prompts the help message. Following it with a command name shows only the help for that command.",
	   'question':
	   "`k!question add (Question?) [time]`: Add your own question, you can set the time limit from 10 to 30 seconds. 15 seconds is default.",
	   'questions':
	   "`k!questions [search] [by:UserID or User#1234]`: View all the questions, sorted by the number of collections they're in. Supports search, *don't mention people when searching for them.*",
	   'collection':
	   "`k!collection create`: Create a collection of questions. You'll need to find questions to add by searching for them, this works the same way as `k!question`, without the command.",
	   'collections':
	   "`k!collections`: View all collections, sorted by ratings.",
	   'ratings':
	   "`k!ratings [clear]`: View all ratings you've left on collections of questions. Use `clear` if you want them erased.",
	   'feedback':
	   "`k!feedback (Your feedback)`: Give feedback directly to the developers, we might get in touch with you.",
	   'privacy':
	   "`k!privacy`: Reads you your privacy policy for the external portion of Kahoot.Discord's functionality."}

games={}
authcodes={}

verbose,logchannel,modchannel,apiurl,apiport,ver,lastver,changes,superusers=(None,)*9
questions,collections,ratings=(None,)*3

def reload():
	global verbose,logchannel,modchannel,apiurl,apiport,ver,lastver,changes,superusers
	global questions,collections,ratings
	
	print('reading config...')
	config.read(datafolder+'config.ini')

	#settings
	verbose=config.getint('settings','verbose')
	logchannel=config.getint('settings','logchannel')
	modchannel=config.getint('settings','modchannel')
	apiurl=config.get('settings','apiurl')
	apiport=config.getint('settings','apiport')
	
	#versioning
	ver=config.get('settings','ver')
	lastver=config.get('settings','lastver')
	with open(datafolder+'changes.txt', 'r', encoding='utf-8') as file:
		changes=file.readlines()
	
	#kahoot
	questions={id:literal_eval(config.get('questions',id)) for id in config['questions']}
	collections={id:literal_eval(config.get('collections',id)) for id in config['collections']}
	ratings={id:literal_eval(config.get('ratings',id)) for id in config['ratings']}
	
	superusers=[int(superuser) for superuser in config.get('settings','superusers').split(',')]
	print('config read!')

def save():
	with open(datafolder+'config.ini','w') as f:
		config.write(f)
	print('config saved!')

reload()