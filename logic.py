import config, genimg
import discord
from discord.ext import commands
from random import randint, choice, shuffle
import asyncio, time, math

ordinal = lambda n: "%d%s" % (n,"tsnrhtdd"[(math.floor(n/10)%10!=1)*(n%10<4)*n%10::4])

class Game:
	def __init__(self,channel,state=0,countdown=-1,waitingplayers=[],lobbyplayers=[],questions=[],scoreboard={},lobbymsg=None,lead=""):
		self.channel=channel
		self.state=state
		self.countdown=countdown
		self.waitingplayers=waitingplayers
		self.lobbyplayers=lobbyplayers
		self.questions=questions
		self.scoreboard=scoreboard
		self.lobbymsg=lobbymsg
		self.lead=lead
	def players(self):
		return self.waitingplayers + self.lobbyplayers
	def raw_players(self):
		return [player.player for player in self.players()]
	def playerlist(self):
		return ["Ready! "+player.name for player in self.lobbyplayers]+["Joining... "+player.name for player in self.waitingplayers]
	def __del__(self):
		for i in self.players():
			if i.auth in config.authcodes: del config.authcodes[i.auth]
			del i
		for i in self.questions:
			del i

class Question:
	def __init__(self,question,duration=15,answers=[],answerstrings=[]):
		self.question=question
		self.duration=duration
		self.answers=answers
		self.answerstrings=answerstrings

class Player:
	def __init__(self,auth,game,player,ip=None,lead="",score=0,answer=-1,anstime=-1,streak=0):
		self.auth=auth
		self.ip=ip
		self.game=game
		self.channel=game.channel
		self.player=player
		self.name=player.name+'#'+player.discriminator
		self.lead=lead
		self.score=score
		self.answer=answer
		self.anstime=anstime
		self.streak=streak
		
		self.is_ready=False
	def ready(self):
		del self.game.waitingplayers[self.game.waitingplayers.index(self)]
		self.game.lobbyplayers.append(self)
		self.is_ready=True
	def countscore(self):
		question = self.game.questions[-1]
		if self.answer in question.answers:
			self.streak+=1
			self.score+=round((self.anstime/question.duration)*1000)+100*self.streak
			return True
		else:
			self.streak=0
			return False

class Logic(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		config.games={}
		config.authcodes={}
		self.delet=[]
	
	async def gamecleanup(self,ctx):
		print('cleaning up...')
		if ctx.channel in config.games:
			for player in config.games[ctx.channel].players():
				if player.auth in config.authcodes:
					del config.authcodes[player.auth]
			del config.games[ctx.channel]
		for msg in self.delet:
			await msg.delete()
		self.delet=[]
	
	async def updatestatus(self,game,status=None):
		if status is None:
			status=game.lobbymsg.content[0:game.lobbymsg.content.find('React')-1]
		if status!=game.lobbymsg.content:
			status+=f"\nReact to join!```{chr(10).join(game.playerlist()) if len(game.players())>0 else 'React to join!'}```"
			try:
				await game.lobbymsg.edit(content=status)
				return True
			except:
				print('failed to edit lobbymsg, giving up.')
				return False
		else:
			return True
	
	async def inviteplayers(self,channel,player):
		if channel in config.games:
			game=config.games[channel]
			if player not in game.raw_players() and player!=self.bot.user:
				auth=str(hex(randint(2**16,2**20-1)))[2:]
				while auth in config.authcodes:
					auth=str(hex(randint(2**16,2**20-1)))[2:]
				#try:
				tmpmsg=await player.send(f"Join the game here; {config.apiurl}{auth} then, return to {game.channel.mention} for the questions!\n"+\
										  "**Note:** this link is designed to uniquely identify your account, don't share this link with other people.\n"+\
										  "If you're concerned, you might wanna read the `k!privacy` policy before you click this link.")
				self.delet.append(tmpmsg)
				p=Player(auth,game,player)
				game.waitingplayers.append(p)
				config.authcodes[auth]=p
				#except:
					#self.delet.append(await game.channel.send(player.mention+", I wasn't able to DM you... Change your privacy settings and try again another time."))
				await self.updatestatus(game)
			else:
				print(player.display_name+"'s reaction was ignored.")
	
	@commands.command(pass_context=True, no_pm=True, aliases=['play','start','game'])
	async def kahoot(self, ctx, timeout='60'):
		if config.verbose: print('kahoot command')
		try: timeout=int(timeout)
		except: timeout=60
		timeout=time.time()+timeout
		
		if ctx.channel in config.games:
			#await ctx.channel.send("It appears that another game is already running in this channel. Please wait until later.")
			#return
			print('[WARN] A game is already running in this channel. It has been overwritten.')
		
		game=Game(ctx.channel,0,timeout)
		config.games[ctx.channel]=game #init state
		
		game.lobbymsg=await ctx.channel.send(f"A game of Kahoot is starting in {round(timeout-time.time())} seconds! Use any reaction to join!")
		await game.lobbymsg.add_reaction('👌')
		
		while timeout>time.time() or len(game.lobbyplayers)<math.ceil(len(game.players())/2):
			if timeout>time.time():
				game.lead=f"A game of Kahoot is starting in {round(timeout-time.time())} seconds!"
				game.state,game.countdown = 1,round(timeout-time.time()) #lobby
			elif time.time()>timeout+60: break
			else:
				game.lead=f"Waiting for more players... ({len(game.lobbyplayers)} joined, {math.ceil(len(game.players())/2)} required, {len(game.players())} total)"
				game.state,game.countdown=1.5,round(timeout+60-time.time()) #waiting for players
			if not await self.updatestatus(game,game.lead):
				await self.gamecleanup(ctx)
				return
			
		if len(game.lobbyplayers)<1:
			await ctx.channel.send("No players! Try again later.")
			await self.gamecleanup(ctx)
			return
		
		if not await self.updatestatus(game,"A game of Kahoot is running right now!"):
			await self.gamecleanup(ctx)
			return
		
		game.state=2 #selecting collection
		
		colopt="0: Random - A random selection of all the questions in Kahoot.Discord."
		colans={}
		i=0
		for id,col in config.collections.items():
			i=i+1
			colopt+=f"\n{i}: {col[0]}"
			colans[i]=col
		
		msg=await ctx.channel.send(f"{ctx.message.author.mention}, choose a collection by sending the associated number;\n```{colopt}```")
		def check(m):
			return m.author==ctx.message.author and m.content.isdigit()
		try: opt=await self.bot.wait_for('message',check=check,timeout=60)
		except asyncio.TimeoutError:
			await ctx.channel.send(content="You took too long. Kahoot cancelled.")
			await self.gamecleanup(ctx)
			return
		opt=int(opt.content)
		
		#try:
		if opt>0: qlist=colans[opt][1]
		else:
			qlist=list(config.questions.keys())
			shuffle(qlist)
			qlist=qlist[:10]
		
		for qid in qlist:
			game.countdown=5
			game.state=3
			qmsg=await ctx.channel.send(f"**Next question in {game.countdown} seconds...**")
			while game.countdown>0:
				await asyncio.sleep(0.75)
				game.countdown-=1
				await qmsg.edit(content=f"**Next question in {game.countdown} seconds...**")
			
			question=Question(question=config.questions[qid][1],duration=config.questions[qid][3],answerstrings=config.questions[qid][2])
			timeout=time.time()+config.questions[qid][3]
			game.state,game.countdown=4,question.duration #ingame
			game.questions.append(question)
			
			em=discord.Embed(title=question.question)
			em.set_image(url=f"{config.apiurl}questions/{qid}.png?v={config.ver}")
			await qmsg.edit(content=f"⏰ {round(timeout-time.time())}",embed=em)
			
			while time.time()<timeout:
				await asyncio.sleep(0.75)
				game.countdown=round(timeout-time.time()) #ingame
				await qmsg.edit(content=f"⏰ {round(timeout-time.time())}")
			
			
			ans = config.questions[qid][0]
			right=[]
			for i, correct in enumerate(ans):
				if correct=='1':
					right.append(i)
			question.answers=right
			
			leaders={}
			for player in game.lobbyplayers: #reward points to good boys
				player.countscore()
				leaders[player]=player.score
				player.answer=-1
				player.anstime=-1
			
			leaderboard=''
			places={}
			ordlead=dict(enumerate(sorted(leaders,key=leaders.get,reverse=True)))
			for i,player in enumerate(sorted(leaders,key=leaders.get,reverse=True)):
				leaderboard+=f"{player.name} ({ordinal(i+1)}): {leaders[player]}\n"
				if i==0:
					player.lead="You're in 1st place! "
					if len(ordlead)>1: player.lead+=f"{leaders[player]-leaders[ordlead[1]]} points ahead of {ordlead[1].name}!"
				else:
					player.lead=f"You're in {ordinal(i+1)} place! {leaders[ordlead[i-1]]-leaders[player]} points behind {ordlead[i-1].name}!"
			
			await ctx.channel.send('Current leaderboard:```'+leaderboard+'```')
			
			timeout=5
			game.state,game.countdown,game.scoreboard=5,5,leaderboard #show results
			while timeout>0:
				game.countdown=timeout
				await asyncio.sleep(0.75)
				timeout-=1
		
		# except Exception as e:
			# print(e)
			# await ctx.channel.send("Whoops! Kahoot has crashed, the developers will be right on to it. Try again later.")
		
		await ctx.channel.send("Game over.")
		await self.gamecleanup(ctx)