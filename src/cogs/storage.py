from discord.ext import commands
from discord import Embed
import discord, os, re, typing

class StorageCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.playlistPath = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'Playlists/')


	@commands.command(name='createPlaylist')
	async def createPlaylist(self, ctx, playlistName):
		"""[playlist] - create playlist with this name"""
		res = re.match(os.getenv('FILE_NAME_REGEX'), playlistName)

		if (res == None):
			await ctx.send("Only alphanumeric and underscores allowed in name")
			return

		name = self.playlistPath + playlistName + ".txt"

		if (os.path.exists(name)):
			await ctx.send("Playlist already exists")
			return

		with open(name, "w") as f:
			await ctx.send("Playlist created successfully")

	@commands.command(name='removePlaylist')
	async def removePlaylist(self, ctx, playlistName):
		"""[playlist] - remove playlist with this name"""
		name = self.playlistPath + playlistName + ".txt"

		if (not(os.path.exists(name))):
			await ctx.send("Playlist doesn't exist")
			return

		os.remove(name)

		await ctx.send(playlistName + " removed successfully")

	@commands.command(name='showPlaylists')
	async def showPlaylists(self, ctx):
		"""Show all playlists"""
		ls = []

		for (dirpath, dirnames, filenames) in os.walk(self.playlistPath):
			ls.extend(filenames)
			break

		embed = Embed(color=discord.Color.blurple())
		embed.title = "Playlists"
		embed.description = "There are no playlists" if (len(ls) == 0) else '\n'.join(list(map(lambda p: p[:-4], ls)))

		await ctx.send(embed=embed)

	@commands.command(name='describePlaylist')
	async def describePlaylist(self, ctx, playlistName):
		"""[playlist] - show songs in this playlist"""
		name = self.playlistPath + playlistName + ".txt"

		if (not(os.path.exists(name))):
			await ctx.send("Playlist doesen't exist")
			return

		embed = Embed(color=discord.Color.blurple())
		embed.title = playlistName
		desc = ""
		with open(name, 'r') as the_file:
			desc = the_file.read()

		embed.description = "Empty Playlist" if (desc == "") else desc

		await ctx.send(embed=embed)

	@commands.command(name='addSong')
	async def addSong(self, ctx, playlistName, *, songName):
		"""[playlist][song] - add song to playlist"""
		name = self.playlistPath + playlistName + ".txt"

		if (not(os.path.exists(name))):
			await ctx.send("Playlist doesen't exist")
			return

		# check if song already exists
		lines = []
		with open(name, 'r') as the_file:
			lines = the_file.readlines()

		for line in lines:
			if (line.strip("\n") == songName):
				await ctx.send("Song already present")
				return

		with open(name, 'a') as the_file:
			the_file.write(songName + '\n')

		await ctx.send("Song added successfully")

	@commands.command(name='removeSong')
	async def removeSong(self, ctx, playlistName, *, songName):
		"""[playlist][song] - remove song from playlist"""
		name = self.playlistPath + playlistName + ".txt"

		if (not(os.path.exists(name))):
			await ctx.send("Playlist doesen't exist")
			return

		lines = []
		with open(name, 'r') as the_file:
			lines = the_file.readlines()

		removed = False
		with open(name, 'w') as the_file:
			for line in lines:
				if (line.strip('\n') != songName):
					the_file.write(line)

				else:
					removed = True

		if (removed):
			await ctx.send(songName + " removed from " + playlistName)

		else:
			await ctx.send(songName + " not found in " + playlistName)

def setup(bot):
	bot.add_cog(StorageCog(bot))