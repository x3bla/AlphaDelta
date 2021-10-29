import discord
from discord.ext import commands
from cogs.video.downloader import *
from cogs.video.videodata import *
from cogs.video.videoqueue import *
from cogs.video.autoplay import *

class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music is loaded")

    # commands starts here
    @commands.command(name="loop")
    async def loop_(self, ctx):

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

        try:  # if bot is not in VC, join it
            await channel.connect()
        except discord.ClientException:
            pass

        if title.lower() == "queue" or title.lower() == "q":
            # TODO: play the queue and enable autoplay
            return

        data = await videodata.getVideoData(title)  # getting all of the data beforehand, song title, id, etc
        current_song = data['title']
        queue = videoqueue.VideoQueue()

        server = ctx.message.guild  # the server where the command is sent
        voice_channel = server.voice_client  # the voice channel of the user who sent the command
        print(server)

        if queue.displayQueue(server):
            auto_play_flag = True
        try:
            voice_channel.stop()  # ends the current song if there is
        except voice_channel.ClientException:
            pass

        async with ctx.typing():
            temp = VideoQueueItem(VideoData(data))  # downloading, classes are troublesome
            await temp.download()

            voice_channel.play(discord.FFmpegOpusAudio(ytdl.prepare_filename(data)))  # play song

            autoplay = AutoPlay(server)
            if autoplay.loop:
                queue.addVideo(server, current_song)  # adding back into the queue if loop is True
            # TODO: MOVE DEL LINE TO AUTOPLAY
            # await queue.removeVideo(server, 0)  # removing first video from list since it's playing
            await ctx.send(f"**Now playing:** {current_song}")

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
            await ctx.send(f"**Now playing:** {ctx}")
        except discord.VoiceClient:
            await ctx.send("There is no song to skip")

    @commands.command(name="queue", aliases=['q'])
    async def queue_(self, ctx, *, title):

        # check if a song is playing before queueing
        # queue.append(title)
        await ctx.send(f"`{title}` added to queue")

    @commands.command(aliases=['r'])
    async def remove(self, ctx, songIndex):
        server = ctx.message.guild
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
