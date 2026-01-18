import asyncio
import os
import random

import discord
from discord.ext import commands

from .platform import youtube, spotify, soundcloud

"""
New overhaul plan. this music.py will be middle man handling the playing audio on discord
and reading the commands from slash commands (maybe) or `!p`
it will handle the song requests, send whatever to the relevant backend (youtube, spotify, soundcloud)
and receive the Opus audio or some audio shit, and stream it to the client. internet should be fast enough
or I'll have to download which will cause some... complexity

BUGS:
when you play a song and instantly disconnect the bot, the audio file is downloaded but not removed.
and the file remains open until the bot is restarted
"""


servers = {}


class VideoData:
    def __init__(self, title, url, duration, data, platform=0):
        self.title = title
        self.url = url
        self.duration = duration
        self.platform = platform  # 0: YouTube, 1: Spotify, 2: Soundcloud
        self.data = data  # just in case

    def __str__(self):
        return [self.title, self.url, self.duration, self.platform]


class ServerQueue:
    def __init__(self, video_data: VideoData = None):
        self._loop = False
        self._queue = [video_data] if video_data is not None else []

    def shuffle(self) -> list:
        random.shuffle(self._queue)
        return self._queue.copy()

    def loop(self) -> bool:
        self._loop = not self._loop
        return self._loop

    def add(self, data: VideoData) -> list:
        self._queue.append(data)
        return self._queue.copy()

    def remove(self, item) -> list:
        if isinstance(item, VideoData):
            self._queue.remove(item)
        elif isinstance(item, int):
            self._queue.pop(item)
        else:
            print("alarmmmmm remove didn't work correctly")
        return self._queue.copy()

    def get_queue(self) -> list:
        return self._queue.copy()  # just in case, to prevent mutation

    def get_loop(self) -> bool:
        return self._loop


async def play_time(song_list: list):
    total_playtime = 0
    for duration in song_list:
        total_playtime += duration
    if total_playtime > 3600:
        hour = total_playtime // 3600
        minute = (total_playtime - (hour * 3600)) // 60
        second = (total_playtime - (hour * 3600)) % 60
        return hour, minute, second
    else:
        minute = total_playtime // 60
        second = total_playtime % 60
        return None, minute, second


async def start_playing(ctx):
    server = ctx.message.guild
    if len(servers[server.id].get_queue()) == 0:  # idk
        print("how did I get here")
        return

    voice_channel = server.voice_client
    server = servers[server.id]
    server_queue = server.get_queue()

    while len(server_queue) != 0:
        async with ctx.typing():
            _, minutes, seconds = await play_time([server_queue[0].duration])
            data = server_queue[0].data
            url = server_queue[0].url
            current_song = server_queue[0].title
            file_name = await youtube.get_file(url)  # download

            source = discord.FFmpegPCMAudio(file_name)
            source = discord.PCMVolumeTransformer(source, volume=0.5)
            voice_channel.play(source)  # play song

            # embed
            embed = discord.Embed(title="Now Playing:",
                                  description=f"[{current_song}]({url})",
                                  color=0x871478)
            embed.set_thumbnail(url=data["thumbnail"])
            embed.add_field(name="Video Duration", value=str(minutes) + "m " + str(seconds) + "s", inline=False)
            await ctx.send(embed=embed)

        await delete_audio_file(ctx, file_name)

        if server.get_loop():
            server.add(server_queue[0])

        try:
            server.remove(server_queue[0])
        except ValueError:
            pass  # no idea why they deleted the current song but oh wells

        server_queue = server.get_queue()  # refresh queue


async def delete_audio_file(ctx, file_name):
    """deletes song at the end of the song"""
    while True:
        try:
            while ctx.message.guild.voice_client.is_playing():
                await asyncio.sleep(2)
                pass
            await asyncio.sleep(2)
            print("[info] attempting to remove", file_name)
            os.remove(file_name)
            print("[info] Successfully removed", file_name)
            break
        except AttributeError:
            while True:  # if the bot leaves after joining instantly, need delay to remove audio
                try:
                    os.remove(file_name)
                    break
                except PermissionError:
                    await asyncio.sleep(60)
            break

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music is loaded")

    # commands starts here
    @commands.command(name="loop")
    async def toggle_loop(self, ctx):
        server_id = ctx.message.guild.id
        if server_id not in servers:
            servers[server_id] = ServerQueue()

        queue = servers.get(server_id)
        loop = queue.loop()
        if loop:
            await ctx.send("Loop mode is now **enabled**")
        else:
            await ctx.send("Loop mode is now **disabled**")


    @commands.command(aliases=['p'])
    async def play(self, ctx, *, search_string=None):
        # check if arguments are valid
        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        elif search_string is None:
            await ctx.send("You need to type in a song or a url with `!play song`")
            return

        elif "playlist?" in search_string:
            await ctx.send("For playlists, use the `!queue` command instead (not implemented ping my creator)")
            return

        else:
            channel = ctx.message.author.voice.channel
            try:  # if bot is not in VC, join it
                await channel.connect()
            except discord.ClientException:
                pass

        if "http" not in search_string:
            if ":" in search_string:
                search_string = search_string.replace(":", "")

        # create server queue
        server_id = ctx.message.guild.id
        if server_id not in servers:
            servers[server_id] = ServerQueue()
        server = servers[server_id]


        # TODO: playlist
        # if 'entries' in data:
        #     # take first item from a playlist
        #     data = data['entries'][0]

        data = await youtube.get_info(search_string)  # getting all the data, song title, id, etc
        if data is False:
            await ctx.send("Please limit your video length to below **1 hour**")
            return
        elif data is None:  # possible reason: searching up channel name instead of song
            await ctx.send("Can't find song, please reword")
            return

        # youtube
        title = data["title"]
        url = data["original_url"]
        duration = data["duration"]
        if len(server.get_queue()) == 0:
            server.add(VideoData(title, url, duration, data))
            await start_playing(ctx)

        else:
            server.add(VideoData(title, url, duration, data))

            queue_number = len(server.get_queue())
            _, minutes, seconds = await play_time([duration])

            # embed
            embed = discord.Embed(title=title, url=url, color=0x871478)
            embed.set_thumbnail(url=data["thumbnail"])
            embed.add_field(name="Queue no.", value=str(queue_number), inline=True)
            embed.add_field(name="Video Duration", value=str(minutes) + "m " + str(seconds) + "s", inline=True)
            await ctx.send(embed=embed)

    @commands.command(aliases=["stop"])
    async def pause(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.pause()

    @commands.command()
    async def resume(self, ctx):
        server = ctx.message.guild
        voice_channel = server.voice_client

        voice_channel.resume()

    @commands.command(aliases=['s'])
    async def skip(self, ctx):
        server = servers.get(ctx.message.guild.id)
        if not server:
            await ctx.send("there's no song in the queue to play")
            return

        voice_channel = ctx.message.guild.voice_client
        server_queue = server.get_queue()

        try:
            voice_channel.stop()
            await ctx.send("**skipping...**")
        except discord.VoiceClient:
            await ctx.send("There is no song to skip")

        if len(server_queue) == 0:
            await ctx.send("there's no song in the queue to play")

    @commands.command(aliases=["sh"])
    async def shuffle(self, ctx):
        server = servers.get(ctx.message.guild.id)
        if not server:
            await ctx.send("there's no song in the queue to shuffle")
            return

        if len(server.get_queue()) == 0:
            await ctx.send("there's no song in the queue to shuffle")
            return

        server.shuffle()
        await ctx.send("**Shuffled** :twisted_rightwards_arrows:")

    @commands.command(aliases=['r'])
    async def remove(self, ctx, song_index):
        server_id = ctx.message.guild.id
        song_index = int(song_index) - 1  # -1 cuz index starts at 0
        server = servers.get(server_id)
        server_queue = server.get_queue()

        if not server or len(server_queue) == 0:
            await ctx.send(f"{ctx.author.mention} Your queue is empty")
            return
        elif song_index < 0:
            await ctx.send(f"{ctx.author.mention} https://tenor.com/view/vir-das-wtf-bro-wtf-wtf-bro-bro-wtf-gif-24602109")
            return
        elif len(server_queue) < song_index+1:
            await ctx.send(f"{ctx.author.mention} Your number exceeds the queue")
            return

        title = server.get_queue()[song_index].title
        server.remove(song_index)

        server_queue = server.get_queue()  # get new list
        vid_queue = ''
        playtime_list = []
        num = 0

        for song in server_queue:
            minutes = song.duration // 60
            seconds = song.duration % 60
            num += 1  # 1. title 2:10
            playtime_list.append(song.duration)
            vid_queue = vid_queue + str(num) + ". " + song.title + " " + str(minutes) + ":" + str(seconds) + "\n"

        hour, minute, second = await play_time(playtime_list)
        if hour is None:
            total_play_time = str(minute) + "m " + str(second) + "s"
        else:
            total_play_time = str(hour) + "h " + str(minute) + "m " + str(second) + "s"

        await ctx.send(f"Removed `{title}`! your queue is now:\n"
                       f"```{vid_queue}\nTotal play time: {total_play_time}```")

    @commands.command(aliases=['v', "list"])
    async def view(self, ctx):
        server_id = ctx.message.guild.id
        if not servers.get(server_id) or len(servers.get(server_id).get_queue()) == 0:
            await ctx.send("The queue is empty")
            return


        server_queue = servers.get(server_id).get_queue()
        playtime_list = []
        vid_queue = ''
        num = 0

        for song in server_queue:
            minutes = song.duration // 60
            seconds = song.duration % 60
            playtime_list.append(song.duration)
            num += 1  # 1. title 2:10
            vid_queue = vid_queue+str(num)+". "+song.title+" "+str(minutes)+":"+str(seconds)+"\n"
        if num == 0:
            await ctx.send("your queue is empty")
        else:
            hour, minute, second = await play_time(playtime_list)
            if hour is None:
                total_play_time = str(minute) + "m " + str(second) + "s"
            else:
                total_play_time = str(hour) + "h " + str(minute) + "m " + str(second) + "s"
            await ctx.send(f"```{vid_queue}\nTotal play time: {total_play_time}```")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        try:
            voice_client = ctx.message.guild.voice_client
            await voice_client.disconnect()
            await ctx.send("Bye!")
        except AttributeError:
            await ctx.send("But I'm not in a voice channel?")

    @commands.command(aliases=["var", "vars"])
    async def variables(self, ctx):
        queue = []
        for song in servers[ctx.message.guild.id].get_queue():
            queue.append(song.title)
        await ctx.send(f"loop: {servers[ctx.message.guild.id].get_loop()}\nqueue: {queue}")


async def setup(bot):
    await bot.add_cog(Music(bot))
