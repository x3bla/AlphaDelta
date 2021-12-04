import random

import discord
from discord.ext import commands
import yt_dlp
import asyncio
import os

"""
Why did you come back to this absolute mess of a code. 
Basically, you tried to use classes and objects to get and store data as they are queued
as in throw objects with a lot of attributes and dicts into a list
yea, can't do that, data.title brings up an attribute error. So, a lot of classes are useless and removed
but a lot has been built upon them already, and I can't be bothered to overhaul it.

BUGS:
when you play a song and instantly disconnect the bot, the audio file is downloaded but not removed.
and the file remains open until the bot is restarted
"""

yt_dlp.utils.bug_reports_message = lambda: ''  # no idea what this does

# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#post-processing-options
ytdlp_format_options = {  # sets the quality of the audio
    'format': 'worstaudio',
    'outtmpl': 'zz-%(id)s-%(title)s.%(ext)s',  # z to put it at the most bottom
    'restrictfilenames': True,
    'noplaylist': False,
    'ignoreerrors': True,
    'logtostderr': False,
    # 'concurrent_fragment_downloads': 5,  # parallel downloading, if needed
    # 'max_filesize': 5000000,  # 5MB bytes | look at getVideoData
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}  # spam of comments to see which is unneeded

ytdl = yt_dlp.YoutubeDL(ytdlp_format_options)  # loading youtube download options
queue = {}
looping = False

def getServerQueue(server):  # too lazy to remove
    return queue[server]

def addVideo(server, song_title, duration):
    queue[server]["song"].append([song_title, duration])

def createServerQueue(server):
    queue[server] = {
        "loop": False,
        "auto_play_flag": False,
        "song": [],
    }

def playTime(song_list):
    TotalPlaytime = 0
    for duration in song_list:
        TotalPlaytime += duration
    if TotalPlaytime > 3600:
        hour = TotalPlaytime // 3600
        minute = (TotalPlaytime - (hour * 3600)) // 60
        second = (TotalPlaytime - (hour * 3600)) % 60
        return hour, minute, second
    else:
        minute = TotalPlaytime // 60
        second = TotalPlaytime % 60
        return None, minute, second

async def removeVideo(server, videoItem: int):
    del(queue[server]["song"][videoItem])

async def getVideoData(searchString: str, download=False):  # throwing search in to get a ton of data
    data = ytdl.extract_info(searchString, download=download)
    entries = data.get('entries')
    if entries is not None:
        entry = entries[0] if len(entries) > 0 else None
    else:
        entry = data
    if entry["duration"] > 3600:  # if audio is longer than 1 hour, say no
        return False
    else:
        return entry

class VideoData:  # get title and url from a huge dictionary
    def __init__(self, extractedData):
        self.title = extractedData['title']
        self.url = extractedData['webpage_url']
        self.duration = extractedData['duration']
        if self.title is None or self.url is None:
            raise RuntimeError('The extracted data specified does not have one of the following:'
                               'title, webpage_url')


class VideoQueueItem:  # download the video
    def __init__(self, videoData: VideoData):
        self.videoData = videoData

    async def __download(self):
        ytdl.download([self.videoData.url])  # they use a for loop, so the string breaks down into chars

    async def download(self):
        await self.__download()


class AutoPlay:
    """handles everything related to playing audio"""

    @staticmethod
    async def _play(ctx, data, file_name):
        video = VideoData(data)  # Type 'VideoData' doesn't have expected attribute '__getitem__'
        current_song = video.title  # need to turn it to object here
        # screw my life, it'll be better if I rewrote this whole thing since I can't use classes like I thought

        voice_channel = ctx.message.guild.voice_client  # the voice channel of the user who sent the command

        try:  # try to stop current song to play new song
            voice_channel.stop()
        except discord.ClientException:
            pass

        async with ctx.typing():
            video = VideoQueueItem(video)
            await video.download()

            voice_channel.play(discord.FFmpegOpusAudio(file_name))  # play song

            await ctx.send(f"**Now playing: ** {current_song}")

    async def play_next(self, ctx, song_data):
        """check if song is still playing, if not, _play next and delete file. Try catch for when bot disconnects"""
        global looping

        server = ctx.message.guild.id
        serverQueue = getServerQueue(server)  # getting server
        flag = serverQueue["auto_play_flag"]
        discordBot = ctx.message.guild.voice_client
        autoplay = True

        print("triggering autoplay")
        while autoplay:
            looping = True  # temp variable

            if flag:
                pass
            else:
                autoplay = False

            try:  # when bot leaves while playing, pass the error
                while discordBot.is_playing() or discordBot.is_paused():
                    await asyncio.sleep(2)
                    pass
            except AttributeError:
                print("passing")
                pass

            current_song = song_data["title"]
            if serverQueue["loop"]:
                duration = song_data["duration"]
                addVideo(server, current_song, duration)  # adding back into the queue if loop is True

            try:  # if not in queue, pass
                song_index = serverQueue["song"].index([song_data["title"], song_data["duration"]])
                del(serverQueue["song"][song_index])  # song's played, so, YEET
            except ValueError:
                pass

            if not serverQueue["song"]:  # when the queue is empty, break
                serverQueue["auto_play_flag"] = False
                looping = False  # this variable is temp
                break

            try:
                ctx.message.guild.voice_client.is_playing()
            except AttributeError:
                break

            song_data = await getVideoData(serverQueue["song"][0][0])
            file_name = ytdl.prepare_filename(song_data)
            await self._play(ctx, song_data, file_name)  # _play next song on list
            await self.delete_audio_file(ctx, file_name)

            print("deleted", file_name)
            looping = False

    @staticmethod
    async def delete_audio_file(ctx, file_name):
        """deletes song at the end of the song"""
        while True:
            try:
                while ctx.message.guild.voice_client.is_playing():
                    await asyncio.sleep(2)
                    pass
                await asyncio.sleep(2)
                os.remove(file_name)
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
    async def loop_(self, ctx):
        try:
            server = ctx.message.guild.id
            serverQueue = getServerQueue(server)

            if serverQueue["loop"]:  # index 0 for loop boolean
                await ctx.send("Loop mode is now disabled")
                serverQueue["loop"] = False

            else:
                await ctx.send("Loop mode is now enabled")
                serverQueue["loop"] = True
        except KeyError:
            await ctx.send("You do not have a queue in the server")

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, title=None):
        if not ctx.message.author.voice:  # check if arguments are valid
            await ctx.send("You are not connected to a voice channel")
            return

        elif title is None:
            await ctx.send("You need to type in a song or a url with `!play ")
            return

        elif "playlist?" in title:
            await ctx.send("For playlists, use the `!queue` command instead")
            return

        else:
            channel = ctx.message.author.voice.channel
            try:  # if bot is not in VC, join it
                await channel.connect()
            except discord.ClientException:
                pass

        if "http" not in title:
            if ":" in title:
                title = title.replace(":", "")

        server = ctx.message.guild.id
        if server not in queue:  # i need this cuz dict KeyError. Might have to change the way auto play works
            createServerQueue(server)
        serverQueue = getServerQueue(server)

        if serverQueue["song"]:  # if queue exists, enable auto play
            serverQueue["auto_play_flag"] = True

        if title.lower() == "queue" or title.lower() == "q":
            song_title = serverQueue["song"][0][0]  # changes song data from search title to first item in queue
            song_data = await getVideoData(song_title)
            await AutoPlay().play_next(ctx, song_data)
            return

        try:
            data = await getVideoData(title)  # getting all of the data, song title, id, etc
            if data is False:
                await ctx.send("Please limit your video length to below **1 hour**")
                return

            await AutoPlay().play_next(ctx, data)
        except KeyError:
            pass  # if there's no queue, this will be triggered

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
        voice_channel = ctx.message.guild.voice_client
        serverQueue = getServerQueue(ctx.message.guild.id)

        try:
            voice_channel.stop()
            await ctx.send("**skipping...**")
        except discord.VoiceClient:
            await ctx.send("There is no song to skip")

        if serverQueue["song"]:  # if there's another song to play, play
            serverQueue["auto_play_flag"] = True
        else:
            await ctx.send("there's no song in the queue to play")

    @commands.command(aliases=["sh"])
    async def shuffle(self, ctx):
        server = ctx.message.guild.id
        if server not in queue:
            await ctx.send("You don't have a queue")
            return

        serverQueue = getServerQueue(server)
        random.shuffle(serverQueue["song"])
        await ctx.send("**Shuffled** :twisted_rightwards_arrows:")

    @commands.command(name="queue", aliases=['q'])
    async def queue_(self, ctx, *, search=None):
        if search is None:
            await ctx.send("You need to include the song that you want to queue `!queue song`")
            return
        # TODO: allow playlists
        video_data = await getVideoData(search)
        if video_data is False:
            await ctx.send("Please limit your video length to below **1 hour**")
            return

        song_data = VideoData(video_data)
        server = ctx.message.guild.id
        song_title = song_data.title

        if server not in queue:  # if the key "server's name" does not exist, create it.
            createServerQueue(server)

        serverQueue = getServerQueue(server)
        print(song_data, ctx.message.author)
        serverQueue["song"].append([song_title, song_data.duration])
        print(queue, "\n")

        minutes = song_data.duration // 60
        seconds = song_data.duration % 60

        queue_number = len(serverQueue["song"])

        embed = discord.Embed(title=song_title, url=song_data.url, color=0x871478)
        embed.set_thumbnail(url=video_data["thumbnail"])
        embed.add_field(name="Queue no.", value=str(queue_number), inline=True)
        embed.add_field(name="Video Duration", value=str(minutes)+"m "+str(seconds)+"s", inline=True)
        await ctx.send(embed=embed)

    @commands.command(aliases=['r'])
    async def remove(self, ctx, songIndex):
        server = ctx.message.guild.id
        songIndex = int(songIndex) - 1  # -1 cuz index starts at 0

        try:
            await removeVideo(server, songIndex)
        except KeyError:
            await ctx.send(f"{ctx.author.mention} Your queue is empty or you gave a invalid number")

        serverQueue = getServerQueue(server)  # retrieving queue from class
        vidQueue = ''
        PlaytimeList = []
        num = 0

        for song in serverQueue["song"]:
            minutes = song[1] // 60  # song = ["title", duration]
            seconds = song[1] % 60
            num += 1  # 1. title 2:10
            PlaytimeList.append(song[1])
            vidQueue = vidQueue + str(num) + ". " + song[0] + " " + str(minutes) + ":" + str(seconds) + "\n"
        if num == 0:
            await ctx.send("your queue is empty")
        else:
            hour, minute, second = playTime(PlaytimeList)
            if hour is None:
                totalPlayTime = str(minute) + "m " + str(second) + "s"
            else:
                totalPlayTime = str(hour) + "h " + str(minute) + "m " + str(second) + "s"
            await ctx.send(f"Removed! your queue is now:\n"
                           f"```{vidQueue}\nTotal play time: {totalPlayTime}```")

    @commands.command(aliases=['v', "list"])
    async def view(self, ctx):
        try:
            server = ctx.message.guild.id
            if not getServerQueue(server):
                await ctx.send("your queue is empty")
                return
        except KeyError:
            await ctx.send("The queue is empty")
            return

        serverQueue = getServerQueue(server)
        PlaytimeList = []
        vidQueue = ''
        num = 0

        for song in serverQueue["song"]:
            print(num)
            minutes = song[1] // 60  # song = ["title", duration]
            seconds = song[1] % 60
            PlaytimeList.append(song[1])
            num += 1  # 1. title 2:10
            vidQueue = vidQueue+str(num)+". "+song[0]+" "+str(minutes)+":"+str(seconds)+"\n"
        if num == 0:
            await ctx.send("your queue is empty")
        else:
            hour, minute, second = playTime(PlaytimeList)
            if hour is None:
                totalPlayTime = str(minute) + "m " + str(second) + "s"
            else:
                totalPlayTime = str(hour) + "h " + str(minute) + "m " + str(second) + "s"
            await ctx.send(f"```{vidQueue}\nTotal play time: {totalPlayTime}```")

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
        await ctx.send(f"{queue}\nCurrently looping: {looping}")


def setup(bot):
    bot.add_cog(Music(bot))
