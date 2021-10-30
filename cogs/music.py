import discord
from discord.ext import commands
import yt_dlp
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

    def addVideo(self, server, videoTitle, url):
        if server not in self.queue:  # if the key "server's name" does not exist, create it.
            self.queue[server] = {  # { server_key: {"loop": False, "auto_play_flag": False, "song": ["song_name"]}}
                "loop": False,
                "auto_play_flag": False,
                "song": [[videoTitle, url]]
            }

        else:
            self.queue[server]["song"].append([videoTitle, url])
        print(self.queue, "\n")

    async def removeVideo(self, server, videoItem: int):
        del (self.queue[server]["song"][videoItem])


class AutoPlay:
    """handles everything related to playing audio"""

    def __init__(self, server):
        self.server = server
        self.queue = VideoQueue().displayQueue(server)
        self.loop = self.queue["loop"]
        self.auto_play_flag = self.queue["auto_play_flag"]

    async def play(self, ctx, title):
        data = await getVideoData(title)  # getting all of the data beforehand, song title, id, etc
        current_song = data['title']
        queue = self.queue

        server = self.server  # the server where the command is sent
        voice_channel = server.voice_client  # the voice channel of the user who sent the command

        while queue["auto_play_flag"]:
            async with ctx.typing():
                temp = VideoQueueItem(VideoData(data))  # downloading, classes are troublesome
                await temp.download()

                voice_channel.play(discord.FFmpegOpusAudio(ytdl.prepare_filename(data)))  # play song

                try:  # if there's no queue, ignore loop
                    loop = queue.displayQueue(server)
                    if loop[server]["loop"]:
                        queue.addVideo(server, current_song, data["url"])  # adding back into the queue if loop is True
                except KeyError:
                    pass

                await queue.removeVideo(server, 0)  # removing first video from list since it's playing
                await ctx.send(f"**Now playing:** {current_song}")

    async def play_next(self):
        raise NotImplementedError

    async def skip(self):
        raise NotImplementedError


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
            server = ctx.message.guild
            loop = VideoQueue().displayQueue(ctx.message.guild)

            if loop[0]:  # index 0 for loop boolean
                await ctx.send("Loop mode is now disabled")
                VideoQueue().queue[server]["loop"] = False

            else:
                await ctx.send("Loop mode is now enabled")
                VideoQueue().queue[server]["loop"] = True
        except KeyError:
            await ctx.send("You do not have a queue in the server")

    @commands.command(aliases=['p'])
    async def play(self, ctx, *, title):

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        else:
            channel = ctx.message.author.voice.channel

        try:  # if bot is not in VC, join it
            await channel.connect()
        except discord.ClientException:
            pass

        if title.lower() == "queue" or title.lower() == "q":
            # TODO: play the queue and enable autoplay
            await ctx.send("Feature not implemented. Ping my creator")
            return

        data = await getVideoData(title)  # getting all of the data beforehand, song title, id, etc
        current_song = data['title']
        queue = VideoQueue()

        server = ctx.message.guild  # the server where the command is sent
        voice_channel = server.voice_client  # the voice channel of the user who sent the command

        try:
            voice_channel.stop()  # ends the current song if there is
        except voice_channel.ClientException:
            pass

        async with ctx.typing():
            temp = VideoQueueItem(VideoData(data))  # downloading, classes are troublesome
            await temp.download()

            voice_channel.play(discord.FFmpegOpusAudio(ytdl.prepare_filename(data)))  # play song

            try:  # if there's no queue, ignore loop
                loop = queue.displayQueue(server)
                if loop[server]["loop"]:
                    queue.addVideo(server, current_song, data["url"])  # adding back into the queue if loop is True
            except KeyError:
                pass

            # TODO: MOVE DEL LINE TO AUTOPLAY
            await ctx.send(f"**Now playing:** {current_song}")

        try:
            if queue.displayQueue(server):  # if queue exists, enable auto play
                queue.queue[server]["auto_play_flag"] = True
        except KeyError:
            pass

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
            #   call AutoPlay
            # await ctx.send(f"**Now playing:** {ctx}")
            await ctx.send("Feature not implemented, ping my creator")
        except discord.VoiceClient:
            await ctx.send("There is no song to skip")

    @commands.command(name="queue", aliases=['q'])
    async def queue_(self, ctx, *, search):

        song_data = VideoData(await getVideoData(search))
        server = ctx.message.guild
        VideoQueue().addVideo(server.id, song_data.title, song_data)

        await ctx.send(f"`{song_data.title}` added to queue")

    @queue_.error
    async def queue_error(self, ctx, error):
        await ctx.send("You need to include the song that you want to queue `!queue song`")
        print(error)

    @commands.command(aliases=['r'])
    async def remove(self, ctx, songIndex):
        server = ctx.message.guild.id
        songIndex = int(songIndex) - 1  # -1 cuz index starts at 0

        await VideoQueue().removeVideo(server, songIndex)
        queue = VideoQueue().displayQueue(server)  # retrieving queue from class

        # TODO: prepare embed here

        await ctx.send(f"Your queue is now `{queue}`")

    @remove.error
    async def remove_error(self, ctx, error):  # even if unused, error variable is received
        await ctx.send(f"{ctx.author.mention} Your queue is empty or you gave a invalid number")
        print(error)

    @commands.command(aliases=['v', "list"])
    async def view(self, ctx):
        try:
            server = ctx.message.guild.id
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
