"""
	KahootDiscord - created by Yiays#5930
	https://kahoot.yiays.com
	A Discord port of Kahoot.
"""

import discord, os, traceback, asyncio, importlib, time
import config, genimg
from discord.ext import commands

if config.lastver!=config.ver:
	print('generating question images...')
	for id,q in config.questions.items():
		genimg.make_question(id,q[1],q[2])
	config.config.set('settings','lastver',config.ver)

bot=commands.Bot(command_prefix=commands.when_mentioned_or('kahoot ','k! ','k!'), help_attrs={'enabled':False},case_insensitive=True)
bot.remove_command('help')

print('configuring webserver...')
import webserver
config.modules['webserver']=webserver

import admin
config.modules['admin']=admin
adminclass=admin.Admin(bot)
bot.add_cog(adminclass)

import logic
config.modules['logic']=logic
gameclass=logic.Logic(bot)
bot.add_cog(gameclass)

class Reload(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
	@commands.command(pass_context=True,no_pm=False)
	async def reload(self,ctx,*,module:str):
		if ctx.message.author.id in config.superusers:
			if module=='webserver':
				await config.modules['webserver'].stop()
				webserver=importlib.reload(config.modules[module])
				config.modules['webserver']=webserver
				await webserver.start()
				await ctx.channel.send("reloaded `"+module+"` succesfully!")
			elif module=='config':
				config.reload()
				await ctx.channel.send("reloaded `"+module+"` succesfully!")
			elif module=='logic':
				bot.remove_cog('Logic')
				logic=importlib.reload(config.modules['logic'])
				gameclass=logic.Logic(bot)
				bot.add_cog(gameclass)
			elif module==admin:
				bot.remove_cog('Admin')
				admin=importlib.reload(config.modules['admin'])
				adminclass=admin.Admin(bot)
				bot.add_cog(adminclass)
			elif module in config.modules and config.modules[module]:
				try:
					bot.remove_cog(module.capitalize())
					loadedmodule=importlib.reload(config.modules[module])
					bot.add_cog(getattr(loadedmodule,module.capitalize())(bot))
					await ctx.channel.send("reloaded `"+module+"` succesfully!")
				except AttributeError:
					importlib.reload(config.modules[module])
					await ctx.channel.send("reloaded `"+module+"` succesfully?")
				except Exception as e:
					print(e)
					await ctx.channel.send("reloading `"+module+"` failed.")
			else:
				await ctx.channel.send('`'+module+"` isn't available for reloading.")
		else:
			await emformat.genericmsg(ctx.channel,"this command is restricted.","error","reload")
bot.add_cog(Reload(bot))

@bot.event
async def on_ready():
	print('logged in as')
	print(bot.user.name)
	print(bot.user.id)
	print('------')
	
	if not config.connected:
		await webserver.start()
		config.connected=True
	
	await bot.change_presence(activity=discord.Activity(name='k!kahoot',type=discord.ActivityType.playing))

@bot.event
async def on_error(*args):
	error = traceback.format_exc()
	print(time.strftime("%H:%M:%S",time.localtime())+" - encountered an error;\n"+error)
	if config.logchannel:
		channel = bot.get_channel(config.logchannel)
		await channel.send(time.strftime("%H:%M:%S",time.localtime())+" - **encountered an error;**\n```"+error[:1950]+'```')

@bot.event
async def on_reaction_add(reaction,user):
	if user!=bot.user:
		await adminclass.handle_react(reaction,user)
		await gameclass.inviteplayers(reaction.message.channel,user)

print('connecting...')
bot.run(os.environ.get("KahootDiscord"))

#shutdown

print('exited.')