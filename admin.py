import config, genimg
from discord.ext import commands
from random import randint
import discord, asyncio, math

reaction_numbers = ["\u0030\u20E3","\u0031\u20E3","\u0032\u20E3","\u0033\u20E3","\u0034\u20E3","\u0035\u20E3", "\u0036\u20E3","\u0037\u20E3","\u0038\u20E3","\u0039\u20E3"]

class Question:
	def __init__(self,qid,question,duration=15,answers="",answerstrings=[],creator=None):
		self.qid=qid
		self.question=question
		self.duration=duration
		self.answers=answers
		self.answerstrings=answerstrings
		self.creator=creator

class Admin(commands.Cog):
	def __init__(self,bot):
		self.bot=bot
		self.paginate={}
	
	async def handle_react(self,reaction,user):
		channel=reaction.message.channel
		if channel in self.paginate:
			if reaction.emoji in reaction_numbers:
				print("handling reaction")
				page=reaction_numbers.index(reaction.emoji)
				questions=self.getquestions(page=page,limit=10)
				str=f"Page {page}:```"+"\n".join([f"{i+1+(page-1)*10}: {q.question} {', '.join(q.answerstrings[:-1])} or {q.answerstrings[-1]}." for i,q in enumerate(questions)])+"```"
				if len(str)<=6: str="```None found!```"
				await self.paginate[channel].edit(str)
			await reaction.delete()
		else:
			print("ignored reaction because the channel didn't match up.")
	
	def getquestions(self,page=0,sort=None,search=None,limit=30):
		result=[]
		i=page*limit
		for qid,q in config.questions.items():
			if i in range(page*limit,min(len(config.questions),page*limit+limit)):
				if len(q)>3: #question has an author
					try:
						creator=self.bot.get_user(q[4])
					except:
						creator=None
				result.append(Question(qid,question=q[1],duration=q[3],answers=q[0],answerstrings=q[2],creator=creator))
			else: break
			i+=1
		return result
	
	@commands.command(pass_context=True, no_pm=False, aliases=['?','??'])
	async def help(self, ctx, *, search=None):
		if config.verbose: print('help command')
		embed = discord.Embed(title="k!help", colour=discord.Colour(0x5675a3), url=config.apiurl, description="Kahoot.Discord brings the wonders of Kahoot to group messengers.")
		embed.set_footer(text=f"Kahoot.Discord v{config.ver}", icon_url="https://cdn.discordapp.com/avatars/553870204078260224/1f93a197e4d39a95d97e50a7cd8e6e1d.png")
		for command in config.dhelp:
			if search:
				if command.lower().find(search):
					embed.add_field(name=command, value=config.dhelp[command])
			else: embed.add_field(name=command, value=config.dhelp[command])
		await ctx.channel.send(embed=embed)
	
	@commands.command(pass_context=True, no_pm=False, aliases=['privacypolicy'])
	async def privacy(self,ctx):
		if config.verbose: print('privacy command')
		embed=discord.Embed(title="k!privacy", colour=discord.Colour(0x5675a3), url=config.apiurl, description="Because of the nature of Kahoot, you need to use a website to play. Here's your privacy policy for that site.")
		embed.set_footer(text=f"Kahoot.Discord v{config.ver}", icon_url="https://cdn.discordapp.com/avatars/553870204078260224/1f93a197e4d39a95d97e50a7cd8e6e1d.png")
		embed.add_field(name="When visiting the homepage",value="While visiting the homepage, you are served a static web page and nothing is stored or logged.")
		embed.add_field(name="When playing the game",value="While playing Kahoot with the website in game or seeing the results page, the unique url in the address bar identifies you.")
		embed.add_field(name="What we do with this information",value="**Your IP address isn't used.** The unique code in the URL (looks like `1f2e3`) works alone to associate your choices in the game with your username in Discord. This means it's very important that you don't share this link with other players.")
		await ctx.channel.send(embed=embed)
	
	@commands.group(pass_context=True, no_pm=False, aliases=['q'])
	async def question(self, ctx):
		if ctx.invoked_subcommand is None:
			await ctx.channel.send(config.dhelp['question'])
		return
	@question.command(pass_context=True,name='add')
	async def addquestion(self,ctx,*,question):
		if config.verbose: print('question add command')
		if question[-2:].replace(' ','').isdigit():
			seconds=int(question[-2:])
			question=question[0:-3]
		else: seconds=15
		await ctx.channel.send('Alright, got it. Now, please send between 2 and 4 possible answers as their own messages followed by "Done" or "Cancel".')
		
		def check(m):
			return m.author == ctx.message.author and m.channel == ctx.channel
		msg = await self.bot.wait_for('message', check=check)
		questions=[]
		possibleanswers=[]
		while msg.content.lower()[0:4]!='done' and msg.content.lower()[0:6]!='cancel':
			await msg.add_reaction('👍')
			print("Possible answer added: "+msg.content)
			questions.append(msg.content)
			possibleanswers.append(msg)
			if len(questions)>=4: break
			msg = await self.bot.wait_for('message', check=check)
		if msg.content.lower()[0:6]=='cancel':
			await ctx.channel.send('Alright, your question has been deleted.')
		else:
			if len(questions)>=2 and len(questions)<=4:
				end=await ctx.channel.send('Now, please 👍 react each of the answers that are correct, then 👍 react this message.')
				await end.add_reaction('👍')
				answer='0000'
				def check(reaction,user):
					return user == ctx.message.author and str(reaction.emoji) == '👍'
				try:
					reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
					while reaction.message!=end:
						
						tempans=[]
						if reaction.message in possibleanswers:
							for i,x in enumerate(answer):
								if i==possibleanswers.index(reaction.message):
									x='1'
									print(reaction.message.content+" has been marked as correct.")
								tempans.append(x)
							answer=''.join(tempans)
						else:
							break
						reaction, user = await self.bot.wait_for('reaction_add', timeout=60.0, check=check)
				except asyncio.TimeoutError:
					await ctx.channel.send('I didn\'t catch your thumbs up on the last message in time, '+ctx.message.author.mention+', you\'ll have to start again.')
					return
				id=str(randint(10000,99999))
				while id in list(config.config['questions']):
					id=str(randint(10000,99999))
				config.config.set('questions',id,repr((answer,question,questions,seconds)))
				config.save()
				genimg.make_question(id,question,questions)
				await ctx.channel.send('Done! Here\'s your question; '+config.apiurl+'questions/'+id+'.png')
			else:
				await ctx.channel.send('Please only provide between 2 and 4 possible answers. This is kahoot.')
	@commands.command(pass_context=True)
	async def questions(self,ctx,*,search):
		if len(search)<1:
			ctx.channel.send(config.dhelp['questions'])
			return
		ctx.channel.send("To be implemented...")
	
	@commands.group(pass_context=True,name='collection')
	async def collection(self,ctx):
		if ctx.invoked_subcommand is None:
			await ctx.channel.send(config.dhelp['collection'])
		return
	@collection.command(pass_context=True,name='add')
	async def addcollection(self,ctx,*,collection):
		if config.verbose: print('collection add command')
		if len(collection)<1:
			await ctx.channel.send("Please provide a proper collection name in the command.")
			return
		await ctx.channel.send("Your collection will be named '"+collection+"', now please select some questions.")
		
		questions=self.getquestions(limit=10) #need to sort this eventually
		
		str="Page 1:```"+"\n".join([f"{i+1}: {q.question} {', '.join(q.answerstrings[:-1])} or {q.answerstrings[-1]}." for i,q in enumerate(questions)])+"```"
		if len(str)<=6: str="```None found!```"
		questionselection=await ctx.channel.send(str)
		self.paginate[ctx.channel]=questionselection
		if len(config.questions)>10:
			await ctx.channel.send("React with the page number to see more.")
			for i in range(0,math.ceil(len(config.questions)/10)):
				await questionselection.add_reaction(reaction_numbers[i+1]) #supports a max of 9 pages
		
	@commands.command(pass_context=True)
	async def collections(self,ctx,*,search):
		if len(search)<1:
			ctx.channel.send(config.dhelp['collections'])
			return
		ctx.channel.send("To be implemented...")