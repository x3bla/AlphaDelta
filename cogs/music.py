import discord
from discord.ext import commands
# from discord.voice_client import VoiceClient
import yt_dlp
# import asyncio
# import os


# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#post-processing-options
ytdlp_format_options = {  # sets the quality of the audio
    'format': 'worstaudio',
    'outtmpl': 'zz-%(id)s-%(title)s.%(ext)s',  # z to put it at the most bottom
    'restrictfilenames': True,
    'noplaylist': False,
    # 'concurrent_fragment_downloads': 5,
    'max_filesize': 5000000,  # 5MB bytes
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}  # spam of comments to see which is unneeded


ytdl = yt_dlp.YoutubeDL(ytdlp_format_options)  # loading youtube download options

async def getVideoData(searchString: str, download=False):  # throwing title in to get a ton of data
    data = ytdl.extract_info(searchString, download=download)
    entries = data.get('entries')
    if entries is not None:
        return entries[0] if len(entries) > 0 else None
    else:
        return data

class VideoData:  # getting video's youtube title
    def __init__(self, extractedData):
        self.title = extractedData['title']
        self.url = extractedData['webpage_url']
        if self.title is None or self.url is None:
            raise RuntimeError('The extracted data specified does not have one of the following:'
                               'title, webpage_url')

class VideoQueueItem:  # download the video
    def __init__(self, videoData: VideoData):
        self.videoData = videoData

    async def __download(self):
        parseToList = [self.videoData.url]  # convert to ["song_name"]
        ytdl.download(parseToList)  # they use a for loop, so the string breaks down into chars, どうしてわからない

    async def download(self):
        await self.__download()


class VideoQueue:  # a queue for each server
    """the main queue to add and extract data from a dictionary"""

    queue = {}  # set class as dictionary

    def displayQueue(self, server):
        return self.queue[server]

    def addVideo(self, server, videoTitle):
        if server not in self.queue:  # if the key "server's name" does not exist, create it.
            self.queue[server] = [videoTitle]
        else:
            self.queue[server].append(videoTitle)
        print(self.queue, "\n")

    async def removeVideo(self, server, videoItem: int):
        del(self.queue[server][videoItem])

class AutoPlay:
    """make a flag, while flag: autoplay; else return"""
    def __init__(self, server):
        self.server = server

    async def play(self):
        raise NotImplementedError


loop = False


class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music is loaded")

    # commands starts here
    @commands.command(name="loop")
    async def loop_(self, ctx):
        global loop

        if loop:
            await ctx.send("Loop mode is now disabled")
            loop = False

        else:
            await ctx.send("Loop mode is now enabled")
            loop = True

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, title):
        global loop

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        else:
            channel = ctx.message.author.voice.channel

        try:
            await channel.connect()
        except discord.ClientException:
            pass

        data = await getVideoData(title)  # getting all of the data beforehand, song title, id, etc
        current_song = data['title']
        # queue = VideoQueue()

        server = ctx.message.guild  # the server where the command is sent
        voice_channel = server.voice_client  # the voice channel of the user who sent the command
        print(server)
        # queue.addVideo(server, current_song)

        try:
            voice_channel.stop()  # ends the current song if there is
        except voice_channel.ClientException:
            pass

        async with ctx.typing():
            temp = VideoQueueItem(VideoData(data))  # downloading, classes are troublesome
            await temp.download()

            voice_channel.play(discord.FFmpegOpusAudio(ytdl.prepare_filename(data)))  # play song

            # if loop:
            #     queue.addVideo(server, current_song)  # adding back into the queue if loop is True
            # TODO: MOVE DEL LINE TO AUTOPLAY
            # await queue.removeVideo(server, 0)  # removing first video from list since it's playing
            await ctx.send(f"**Now playing:** {current_song}")

            #
            # reserved for autoplay...?
            #

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
        server = ctx.message.guild
        voice_channel = server.voice_client

        try:
            voice_channel.stop()

            # async with ctx.typing():
            #     player = await YTDLSource.from_url(queue[0], loop=client.loop)  # idk wtf is going on here
            #     voice_channel.play(player, after=lambda e: print("Player error: %s" % e) if e else None)
            #
            #     if loop:
            #         queue.append(queue[0])  # adding back into the queue if loop is True
            #
            #     del (queue[0])
            await ctx.send(f"**Now playing:** {ctx}")
        except discord.VoiceClient:
            await ctx.send("There is no song to skip")

    @commands.command(name="queue", aliases=['q'])
    async def queue_(self, ctx, *, title):

        # check if a song is playing before queueing
        # queue.append(title)
        await ctx.send(f"`{title}` added to queue")

    @commands.command(aliases=['r'])
    async def remove(self, ctx, song):
        raise NotImplementedError
        # del (queue[int(song) - 1])  # -1 cuz index
        # await ctx.send(f"Your queue is now `{queue}`")

    @remove.error
    async def remove_error(self, ctx, error):  # even if unused, error variable is received
        await ctx.send(f"{ctx.author.mention} Your queue is empty or you gave a invalid number")
        print(error)

    @commands.command(aliases=['v', "list"])
    async def view(self, ctx):
        try:
            server = ctx.message.guild
            queue = VideoQueue().displayQueue(server)
            await ctx.send(f"`{queue}`")
        except KeyError:
            await ctx.send("The queue is empty")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        # queue obj
        # queue = []  # erase queue on leave
        voice_client = ctx.message.guild.voice_client
        await voice_client.disconnect()
        await ctx.send("Bye!")

    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("But I'm not in a voice channel?")

    # autoplay feature here probably

def setup(bot):
    bot.add_cog(Music(bot))
