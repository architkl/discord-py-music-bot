import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

bot = commands.Bot(command_prefix=os.getenv('PREFIX'))

@bot.event
async def on_ready():
	print(f'{bot.user} has logged in.')
	bot.load_extension('cogs.music')
	bot.load_extension('cogs.storage')

@bot.command(name='stop')
async def stop(ctx):
	await ctx.send("Bye!")
	await bot.close()
	print("Logged Out")

bot.run(os.getenv('BOT_TOKEN'))