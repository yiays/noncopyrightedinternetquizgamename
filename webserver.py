import json, random, asyncio, time
import config
from pprint import pprint
from aiohttp import web

routes = web.RouteTableDef()

@routes.get("/")
@routes.get("/index.html")
async def index(request):
	if config.verbose: print('GET /')
	with open('web/index.html',encoding='utf8') as f:
		return web.Response(text=f.read().replace('{$config.ver}',config.ver),status=200,headers={'content-type':'text/html'})
@routes.get("/main.css")
async def css(request):
	if config.verbose: print('GET /main.css')
	with open('web/main.css',encoding='utf8') as f:
		return web.Response(text=f.read(),status=200,headers={'content-type':'text/css'})
@routes.get("/main.js")
async def js(request):
	if config.verbose: print('GET /main.js')
	with open('web/main.js',encoding='utf8') as f:
		return web.Response(text=f.read(),status=200,headers={'content-type':'application/javascript'})
@routes.get("/favicon.ico")
async def favicon(request):
	# I don't have one fuck off
	return web.Response(text='',status=404,headers={'content-type':'image/x-icon'})

attempts={}
@asyncio.coroutine
async def auth(request):
	id = str(request.rel_url)[6:]
	print("/auth/"+id)
	if id not in attempts.keys():
		attempts[id]=0
	attempts[id]+=1
	
	if id in config.authcodes:
		if attempts[id]>=3:
			player=config.authcodes[id]
			player.ready()
			with open('web/auth.html',encoding='utf8') as f:
				page=f.read().replace('{target}','/game/'+id)
				return web.Response(text=page,status=200,headers={'content-type':'text/html'})
		else:
			with open('web/auth.html',encoding='utf8') as f:
				page=f.read().replace('{target}','/auth/'+id)
				return web.Response(text=page,status=200,headers={'content-type':'text/html'})
	else: return web.Response(text="Your address is invalid.",status=403)
@asyncio.coroutine
async def game(request):
	id = str(request.rel_url)[6:]
	print("/game/"+id)
	if id in config.authcodes:
		player=config.authcodes[id]
		if player.is_ready:
			with open('web/game.html',encoding='utf8') as f:
				return web.Response(text=f.read(),status=200,headers={'content-type':'text/html'})
		else: return web.Response(text="Try clicking on the invite link in the PM again...",status=403)
	elif id=='demo':
		with open('web/game.html',encoding='utf8') as f:
			return web.Response(text=f.read(),status=200,headers={'content-type':'text/html'})
	else: return web.Response(text="This game is over or you never authorised yourself using the link in the DM.",status=404)
@asyncio.coroutine
async def gamecomm(request):
	id = str(request.rel_url)[6:]
	if id in config.authcodes:
		player=config.authcodes[id]
		data=await request.post()
		if data['cmd']=='getstate': #updates the client on the general state of the game
			state={'player':player.name,'state':player.game.state,'score':player.score,'streak':player.streak}
			if player.game.state==0: #init state
				state.update({'time':-1,'answered':True,'lead':"Game is intializing, you shouldn't be here yet."})
			elif player.game.state==1: #in lobby
				state.update({'time':player.game.countdown,'answered':True,'lead':"Welcome to the lobby for #"+player.channel.name+'!'})
			elif player.game.state==1.5: #waiting for players
				state.update({'time':player.game.countdown,'answered':True,'lead':player.game.lead})
			elif player.game.state==2: #sellecting collection
				state.update({'time':-1,'answered':True,'lead':"The user that started this Kahoot is choosing a category..."})
			elif player.game.state==3: #preparing next question
				state.update({'time':player.game.countdown,'answered':True,'lead':player.lead})
			elif player.game.state==4: #in game
				state.update({'time':player.game.countdown,'answered':(False if player.answer==-1 else True),'lead':player.lead})
			elif player.game.state==5: #show results
				state.update({'time':player.game.countdown,'answered':True,'answers':player.game.questions[-1].answers,'leaderboard':player.game.scoreboard,'lead':player.lead,'streak':player.streak})
			
			if state['lead'] is None or len(state['lead'])<1:
				state['lead']="kahoot rewards speedy answers with more points."
			
			return web.Response(text=json.dumps(state),status=200,headers={'content-type':'application/json'})
		elif data['cmd']=='btn':
			if player.answer==-1 and player.game.state==4: #if the player hasn't answered and we're ingame
				player.answer=int(data['answer'])
				print(f"{player.name} pressed button {data['answer']}")
				return web.Response(status="200")
			if player.game.state==4:print(f"{player.name} pressed button {data['answer']}, but it was already set to {player.answer}")
			else: print(f"{player.name} pressed button {data['answer']} too late, the game is now in state {player.game.state}")
			return web.Response(status="400")
		else:
			return web.Response(text="Bad Request.",status="400")
	elif id=='demo':
		state={'player':'Player#1234','state':5,'score':5480,'streak':3,'time':1,'answered':True,'lead':"Welcome to demo mode!",'answers':[1,2],'leaderboard':"Yiays#5930 (1st): 5480\nDuncan#1234 (2nd): 2456"}
		return web.Response(text=json.dumps(state),status=200,headers={'content-type':'application/json'})
	else: return web.Response(text="Your address is invalid.",status=403)
@routes.get("/game.css")
async def css(request):
	if config.verbose: print('GET /game.css')
	with open('web/game.css',encoding='utf8') as f:
		return web.Response(text=f.read(),status=200,headers={'content-type':'text/css'})
@routes.get("/game.js")
async def js(request):
	if config.verbose: print('GET /game.js')
	with open('web/game.js',encoding='utf8') as f:
		return web.Response(text=f.read(),status=200,headers={'content-type':'application/javascript'})
@routes.get("/results.html")
async def js(request):
	return web.Response(text="I'm still working on the results page, sorry.")
	

app=web.Application()
app.add_routes(routes)
app.router.add_static('/questions',config.datafolder+'questions/')
app.router.add_route('GET', '/auth/{tail:.*}', auth)
app.router.add_route('GET', '/game/{tail:.*}', game)
app.router.add_route('POST', '/game/{tail:.*}', gamecomm)
runner=web.AppRunner(app)

async def start():
	await runner.setup()
	site = web.TCPSite(runner,'0.0.0.0',config.apiport)
	await site.start()
async def stop():
	await runner.cleanup()