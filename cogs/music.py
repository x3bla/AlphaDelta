import discord
from discord.ext import commands
from discord.voice_client import VoiceClient
import yt_dlp
import asyncio
import os

# youtube_dl.utils.bug_reports_message = lambda: ''  # ????

# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#post-processing-options
ytdlp_format_options = {  # sets the quality of the audio
    'format': '249/250/251',  # basically 'worstaudio' but youtube comment said to use this
    'outtmpl': 'zz-%(id)s-%(title)s.%(ext)s',  # z to put it at the most bottom
    # 'restrictfilenames': True,
    'noplaylist': True,
    'concurrent_fragment_downloads': 5,
    # 'keepvideo': False,
    'max_filesize': 5000000,  # in Bytes
    'throttledratelimit': 100000,
    # 'nocheckcertificate': True,
    # 'ignoreerrors': False,
    # 'logtostderr': False,
    # 'quiet': False,
    # 'no_warnings': True,
    'default_search': 'auto',
    # 'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}  # spam of comments to see which is unneeded

ffmpeg_options = {  # idk just don't delete this
    'options': '-vn'
}

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
    def __init__(self, videoSearchString: str, videoData: VideoData):
        self.videoSearchString = videoSearchString
        self.videoData = videoData

    async def __download(self, fileName=None):
        ytdl.download(self.videoData.url)

    async def download(self, fileName=None):        # download is slow because youtube-dl is slow (80KBps)
        await self.__download(self.videoData.url)   # everyone else has slow download speed

    def returnTitle(self):
        return self.videoData.title

    def printThis(self):
        print(f'{self.videoData.title}')

class VideoQueue:  # a queue for each server
    """the main queue to add and extract data from a dictionary"""

    queue = {}  # set class as dictionary

    def displayQueue(self, index):
        raise NotImplementedError

    def addVideo(self, server, videoItem: VideoQueueItem):
        videoTitle = videoItem.returnTitle()  # getting the video's title
        if server not in self.queue:
            self.queue[server] = videoTitle  # if the key "server's name" does not exist, create it
        else:
            self.queue[server].append(videoTitle)

    async def removeVideo(self, videoItem: int):
        # del(self.queue[videoItem])
        print(self.queue[videoItem])

    async def __searchVideo(self, server, searchString: str):
        data = await getVideoData(searchString)
        self.addVideo(server, VideoQueueItem(searchString, VideoData(data)))

    async def searchAndAddVideo(self, server, searchString: str):
        # loop = asyncio.get_event_loop()
        await self.__searchVideo(server, searchString)

class AutoPlay:
    def __init__(self, server):
        self.server = server

    async def play(self):
        raise NotImplementedError

# this class is all copy paste from https://github.com/RK-Coding/Videos/blob/master/rkcodingmusicqueue.py
# class YTDLSource(discord.PCMVolumeTransformer):  # altering this to get info
#     def __init__(self, source, *, data, volume=0.5):
#         super().__init__(source, volume)
#
#         self.data = data
#
#         self.title = data.get('title')
#         self.url = data.get('url')
#
#     @classmethod
#     async def from_url(cls, url, *, loop=None, stream=True):
#         loop = loop or asyncio.get_event_loop()
#         data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
#
#         if 'entries' in data:
#             # take first item from a playlist
#             data = data['entries'][0]
#
#         filename = data['url'] if stream else ytdl.prepare_filename(data)
#         return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)


client = commands.Bot(command_prefix='!')
loop = False


# this is one hell of a library
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

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        else:
            channel = ctx.message.author.voice.channel

        try:
            await channel.connect()
        except discord.ClientException:
            pass

        # for file in os.listdir("./"):  # removing other song files to prevent spam in folder
        #     if file.endswith(".webm"):
        #         os.remove(file)

        data = await getVideoData(title)
        current_song = data['title']
        queue = VideoQueue()

        server = ctx.message.guild  # the server where the command is sent
        voice_channel = server.voice_client  # the voice channel of the user who sent the command
        await queue.searchAndAddVideo(server, title)

        try:
            voice_channel.stop()  # ends the current song if there is
        except voice_channel.ClientException:
            pass

        async with ctx.typing():
            temp = VideoQueueItem(current_song, VideoData(current_song))
            await temp.download()
            # player = await YTDLSource.from_url(queue[0], loop=client.loop)  # idk wtf is going on here
            # voice_channel.play(player, after=lambda e: print("Player error: %s" % e) if e else None)

            for file in os.listdir("./"):  # play the file
                if file.endswith(".webm"):
                    voice_channel.play(discord.FFmpegOpusAudio(file))

            if loop:
                await queue.searchAndAddVideo(server, title)  # adding back into the queue if loop is True

            await queue.removeVideo(0)  # removing first video from list since it's playing
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

    @commands.command(name="queue", alias='q')
    async def queue_(self, ctx, *, title):

        # check if a song is playing before queueing
        # queue.append(title)
        await ctx.send(f"`{title}` added to queue")

    @commands.command(alises=['r'])
    async def remove(self, ctx, song):
        raise NotImplementedError
        # headache here, gl for the classes
        # del (queue[int(song) - 1])  # -1 cuz index
        # await ctx.send(f"Your queue is now `{queue}`")

    @remove.error
    async def remove_error(self, ctx, error):  # even if unused, error variable is received
        await ctx.send(f"{ctx.author.mention} Your queue is empty or you gave a invalid number")

    @commands.command(aliases=['v', "list"])
    async def view(self, ctx):
        # queue obj
        raise NotImplementedError
        # await ctx.send(f"`{queue}`")

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
