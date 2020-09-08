from discord.ext import commands
from discord import utils, Embed
import discord
import lavalink
import os

class MusicCog(commands.Cog):
	""" MusicCog for our bot

		Members:
		bot - commands.Bot
			our bot (handled by the setup function)
		playlistPath - str
			path of the file containing our playlists

		Functions:
		join - connect our bot to a voice channel
		disconnect - disconnect the bot from the voice channel
		play - play the given song
		plPlay - play the given playlist
		pause - pause/resume the player
		next - go to next song
		shuffle - (shuffle/unshuffle) next song is picked up randomly from the queue (the queue is not shuffled!)
		loop - loops the queue
		track_position - get position of current song
		track_hook - disconnect player if no songs are in queue
		connect_to - create websocket for connection to voice channel
		can_interact - check whether the user can interact with the bot
	"""

	def __init__(self, bot):
		self.bot = bot
		self.bot.lavalink = lavalink.Client(self.bot.user.id)
		self.bot.lavalink.add_node("localhost", 2333, "youshallnotpass", "eu", "music-node")
		self.bot.add_listener(self.bot.lavalink.voice_update_handler, "on_socket_response")
		self.bot.lavalink.add_event_hook(self.track_hook)
		self.playlistPath = os.path.join(os.path.dirname(os.path.realpath("__file__")), "Playlists/")

	@commands.command(name="join")
	async def join(self, ctx):
		"""Connects bot to the voice channel of the user who invoked this command"""
		# find user who invoked join command
		member = utils.find(lambda m: m.id == ctx.author.id, ctx.guild.members)

		# check if user is in a voice channel
		if member is not None and member.voice is not None:
			# get voice channel and create player
			vc = member.voice.channel
			player = self.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
			
			if not player.is_connected:
				player.store("channel", ctx.channel.id)
				await self.connect_to(ctx.guild.id, str(vc.id))
				await ctx.send(embed=create_embed("👍  | Connected", color=discord.Color.green()))

		else:
			await ctx.send(embed=create_embed("You're not in a voice channel!", color=discord.Color.orange()))

	@commands.command(aliases=["dc"])
	async def disconnect(self, ctx):
		""" Disconnects the player from the voice channel and clears its queue"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return

		# Clear the queue to ensure old tracks don't start playing
		# when someone else queues something
		player.queue.clear()
		# Stop the current track so Lavalink consumes less resources.
		await player.stop()
		# Disconnect from the voice channel
		await self.connect_to(ctx.guild.id, None)
		await ctx.send(embed=create_embed("*⃣  | Disconnected", color=discord.Color.red()))

	@commands.command(name="play")
	async def play(self, ctx, *, query):
		"""Search for the song and play it"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return
		
		query = f'ytsearch:{query}'

		# use lavalink to search
		results = await player.node.get_tracks(query)

		if not results or not results["tracks"]:
			return await ctx.send(embed=create_embed(f'Nothing found for {query}', color=discord.Color.green()))

		# play the top search result
		track = results["tracks"][0]
		player.add(requester=ctx.author.id, track=track)

		await ctx.send(embed=create_embed("Song queued!", f'[{track["info"]["title"]}] - ({track["info"]["uri"]})'))

		if not player.is_playing:
			await player.play()

	@commands.command(name="plPlay")
	async def plPlay(self, ctx, playlistName):
		"""Play the stored playlist"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return

		name = self.playlistPath + playlistName + ".txt"

		if (not(os.path.exists(name))):
			await ctx.send(embed=create_embed("Playlist doesen't exist", color=discord.Color.orange()))
			return

		# read playlist contents
		with open(name, 'r') as the_file:
			desc = the_file.read()

		if desc == "":
			await ctx.send(embed=create_embed(playlistName, "Empty Playlist"))

		else:
			await ctx.send(embed=create_embed("Now Playing: " + playlistName, desc))

			songs = desc.strip('\n').split('\n')

			# Didn't invoke the play function because it sends notification for each song
			for song in songs:			
				query = f'ytsearch:{song}'

				# use lavalink to search
				results = await player.node.get_tracks(query)

				if not results or not results["tracks"]:
					await ctx.send(embed=create_embed(f'Nothing found for {song}', color=discord.Color.orange()))
					continue

				# play the top search result
				track = results["tracks"][0]
				player.add(requester=ctx.author.id, track=track)

			if not player.is_playing:
				await player.play()

	@commands.command(name="pause")
	async def pause(self, ctx):
		"""Pause / Play the player"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return

		await player.set_pause(not(player.paused))
		await ctx.send(embed=create_embed("Paused!" if player.paused else "Playing!"))

	@commands.command(name="next")
	async def next(self, ctx):
		"""Plays the next song"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return

		await player.skip()
		await ctx.send(embed=create_embed("Skipping current song!"))

	@commands.command(name="shuffle")
	async def shuffle(self, ctx):
		"""Next song is random / in order"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return

		player.set_shuffle(not(player.shuffle))
		await ctx.send(embed=create_embed("Now shuffling tracks!" if player.shuffle else "Now playing tracks in order!"))

	@commands.command(name="loop")
	async def loop(self, ctx):
		"""Loops the queue"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return

		player.set_repeat(not(player.repeat))
		await ctx.send(embed=create_embed("Looping enabled!" if player.repeat else "Looping disabled!"))

	@commands.command(name="trackPosition")
	async def track_position(self, ctx):
		"""Get the current position of song"""
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not (await self.can_interact(ctx)):
			return
		
		# Use format_time from lavalink.utils to convert milliseconds to HH:MM:SS
		await ctx.send(embed=create_embed("Now Playing", str(player.current.title) +":\n" \
			+ lavalink.format_time(player.position) + " / " \
			+ lavalink.format_time(player.current.duration)))

	async def track_hook(self, event):
		if isinstance(event, lavalink.events.QueueEndEvent):
			guild_id = int(event.player.guild_id)
			await self.connect_to(guild_id, None)

	async def connect_to(self, guild_id: int, channel_id: str):
		ws = self.bot._connection._get_websocket(guild_id)
		await ws.voice_state(str(guild_id), channel_id)

	async def can_interact(self, ctx):
		# checks whether the user can interact with the bot
		player = self.bot.lavalink.player_manager.get(ctx.guild.id)

		if not player or not player.is_connected:
			# We can't disconnect, if we're not connected
			await ctx.send(embed=create_embed("Not connected", color=discord.Color.orange()))
			return False

		if not ctx.author.voice or (player.is_connected and ctx.author.voice.channel.id != int(player.channel_id)):
			# Abuse prevention. Users not in voice channels, or not in the same voice channel as the bot
			# may not disconnect the bot
			await ctx.send(embed=create_embed("You\'re not in my voicechannel!", color=discord.Color.orange()))
			return False

		return True

def create_embed(title="", desc="", color=discord.Color.blurple()):
	"""Create embeds with blurple colour"""
	embed = Embed(color=color)
	embed.title = title
	embed.description = desc

	return embed

def setup(bot):
	bot.add_cog(MusicCog(bot))