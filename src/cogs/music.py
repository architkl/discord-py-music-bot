from discord.ext import commands
from discord import utils, Embed
import discord
import lavalink
import os

class MusicCog(commands.Cog):
	def __init__(self, bot):
		self.bot = bot
		self.bot.lavalink = lavalink.Client(self.bot.user.id)
		self.bot.lavalink.add_node('localhost', 2333, 'youshallnotpass', 'eu', 'music-node')
		self.bot.add_listener(self.bot.lavalink.voice_update_handler, 'on_socket_response')
		self.bot.lavalink.add_event_hook(self.track_hook)
		self.playlistPath = os.path.join(os.path.dirname(os.path.realpath('__file__')), 'Playlists/')

	@commands.command(name='join')
	async def join(self, ctx):
		member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)
		if member is not None and member.voice is not None:
			vc = member.voice.channel
			player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
			
			if not player.is_connected:
				player.store('channel', ctx.channel.id)
				await self.connect_to(ctx.guild.id, str(vc.id))
				await ctx.send('👍 | Connected.')

	@commands.command(aliases=['dc'])
	async def disconnect(self, ctx):
		""" Disconnects the player from the voice channel and clears its queue. """
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not player.is_connected:
			# We can't disconnect, if we're not connected.
			return await ctx.send('Not connected.')

		if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
			# Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
			# may not disconnect the bot.
			return await ctx.send('You\'re not in my voicechannel!')

		# Clear the queue to ensure old tracks don't start playing
		# when someone else queues something.
		player.queue.clear()
		# Stop the current track so Lavalink consumes less resources.
		await player.stop()
		# Disconnect from the voice channel.
		await self.connect_to(ctx.guild.id, None)
		await ctx.send('*⃣ | Disconnected.')

	@commands.command(name='play')
	async def play(self, ctx, *, query):
		try:
			player = self.bot.lavalink.player_manager.get(ctx.guild.id)
			query = f'ytsearch:{query}'

			results = await player.node.get_tracks(query)

			if not results or not results['tracks']:
				return await ctx.send('Nothing found!')

			# tracks = results["tracks"][0:10]
			# i = 0
			# query_result = ''
			# for track in tracks:
			# 	i = i + 1
			# 	query_result = query_result  + f'{i}) {track["info"]["title"]} - {track["info"]["uri"]}\n'

			embed = Embed(color=discord.Color.blurple())
			track = results["tracks"][0]			
			embed.title = "Song queued!"
			embed.description = f'[{track["info"]["title"]}] - ({track["info"]["uri"]})'

			# def check(m):
			# 	return m.author.id == ctx.author.id

			# response = await self.bot.wait_for('message', check=check)

			# track = tracks[int(response.content)-1]

			player.add(requester=ctx.author.id, track=track)

			await ctx.send(embed=embed)

			if not player.is_playing:
				await player.play()

		except Exception as e:
			print("Error")
			print(e)

	@commands.command(name='pplay')
	async def pplay(self, ctx, playlistName):
		name = self.playlistPath + playlistName + ".txt"

		if (not(os.path.exists(name))):
			await ctx.send("Playlist doesen't exist")
			return

		embed = Embed(color=discord.Color.blurple())
		embed.title = playlistName
		desc = ""
		with open(name, 'r') as the_file:
			desc = the_file.read()

		if desc == "":
			embed.description = "Empty Playlist"
			await ctx.send(embed=embed)

		else:
			songs = desc.strip('\n').split('\n')

			for song in songs:
				await ctx.invoke(self.bot.get_command('play'), query=song)

	async def track_hook(self, event):
		if isinstance(event, lavalink.events.QueueEndEvent):
			guild_id = int(event.player.guild_id)
			await self.connect_to(guild_id, None)

	async def connect_to(self, guild_id: int, channel_id: str):
		ws = self.bot._connection._get_websocket(guild_id)
		await ws.voice_state(str(guild_id), channel_id)

def setup(bot):
	bot.add_cog(MusicCog(bot))