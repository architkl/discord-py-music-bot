import discord
import traceback
import sys
from discord.ext import commands
from discord import Embed

class ErrorHandlerCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot

	@commands.Cog.listener()
	async def on_command_error(self, ctx, error):
		"""
		Error handler provided by discord.py
		It gets invoked whenever an error event occurs

		Parameters
		----------
		ctx: commands.Context
			The context used for command invocation
		error: commands.CommandError
			The Exception raised
		"""

		if isinstance(error, commands.CommandNotFound):
			await ctx.send(embed=Embed(title=f'Command is invalid.', color=discord.Color.red()))

		elif isinstance(error, commands.MissingRequiredArgument):
			await ctx.send(embed=Embed(title=f'Invalid use of {ctx.command}', color=discord.Color.red()))

		elif isinstance(error, commands.TooManyArguments):
			await ctx.send(embed=Embed(title=f'Invalid use of {ctx.command}', color=discord.Color.red()))

		elif isinstance(error, commands.DisabledCommand):
			await ctx.send(embed=Embed(title=f'{ctx.command} has been disabled.', color=discord.Color.red()))

		else:
			# All other Errors not returned come here. And we can just print the default TraceBack.
			print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
			traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

def setup(bot):
	bot.add_cog(ErrorHandlerCog(bot))