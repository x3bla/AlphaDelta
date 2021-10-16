import discord
from discord.ext import commands
# from discord.voice_client import VoiceClient
import youtube_dl
# import asyncio
import os

#youtube_dl.utils.bug_reports_message = lambda: ''  # ????

# https://github.com/ytdl-org/youtube-dl/blob/master/README.md#post-processing-options
ytdl_format_options = {  # sets the quality of the audio
    'format': '249/250/251',  # basically 'worstaudio' but youtube comment said to use this
    'outtmpl': 'zz-%(id)s-%(title)s.%(ext)s',  # z to put it at the most bottom
    # 'restrictfilenames': True,
    # 'noplaylist': True,
    # 'keepvideo': False,
    'max_filesize': 5000000,  # in Bytes
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

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)  # loading youtube download options


# this class is all copy paste from https://github.com/RK-Coding/Videos/blob/master/rkcodingmusicqueue.py
class YTDLSource(discord.PCMVolumeTransformer):  # altering this to get info
    title = ""
    url = ""

    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

#     @classmethod
#     async def from_url(cls, url, *, loop=None, stream=False):
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
queue = []
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
        global queue

        if not ctx.message.author.voice:
            await ctx.send("You are not connected to a voice channel")
            return

        else:
            channel = ctx.message.author.voice.channel

        try:
            await channel.connect()
        except discord.ClientException:
            pass

        queue.append(title)
        server = ctx.message.guild  # the server where the command is sent
        voice_channel = server.voice_client  # the voice channel of the user who sent the command

        try:
            voice_channel.stop()  # ends the current song if there is
        except voice_channel.ClientException:
            pass
        # add later
        # song_there = os.path.isfile("song.webm")
        # try:
        #     if song_there:
        #         os.remove("song.webm")

        try:
            async with ctx.typing():
                # player = await YTDLSource.from_url(queue[0], loop=client.loop)  # idk wtf is going on here
                # voice_channel.play(player, after=lambda e: print("Player error: %s" % e) if e else None)

                with youtube_dl.YoutubeDL(ytdl_format_options) as ydl:
                    ydl.download([title])
                queue.append(YTDLSource.title)

                for file in os.listdir("./"):
                    if file.endswith(".webm"):
                        os.rename(file, "song.webm")
                voice_channel.play(discord.FFmpegOpusAudio("song.webm"))

                if loop:
                    queue.append(queue[0])  # adding back into the queue if loop is True

                del (queue[0])
                await ctx.send(f"**Now playing:** {playerTitle}")
        except discord.ClientException:  # except: already playing a song
            await ctx.send(f"`{title}` added to queue")

            # reserved for autoplay...?

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

            async with ctx.typing():
                # player = await YTDLSource.from_url(queue[0], loop=client.loop)  # idk wtf is going on here
                # voice_channel.play(player, after=lambda e: print("Player error: %s" % e) if e else None)

                if loop:
                    queue.append(queue[0])  # adding back into the queue if loop is True

                del (queue[0])
            await ctx.send(f"**Now playing:** {player.title}")
        except discord.VoiceClient:
            await ctx.send("There is no song to skip")

    @commands.command(aliases=["queue", 'q'])
    async def queue_(self, ctx, *, title):
        global queue

        queue.append(title)
        await ctx.send(f"`{title}` added to queue")

    @commands.command(alises=['r'])
    async def remove(self, ctx, song):
        global queue

        del (queue[int(song) - 1])  # -1 cuz index
        await ctx.send(f"Your queue is now `{queue}`")

    @remove.error
    async def remove_error(self, ctx, error):  # even if unused, error variable is received
        await ctx.send(f"{ctx.author.mention} Your queue is empty or you gave a invalid number")

    @commands.command(aliases=['v', "list"])
    async def view(self, ctx):
        global queue

        await ctx.send(f"`{queue}`")

    @commands.command(aliases=['l'])
    async def leave(self, ctx):
        global queue
        queue = []  # erase queue on leave
        await ctx.voice_client.disconnect()
        await ctx.send("Bye!")

    @leave.error
    async def leave_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            await ctx.send("But I'm not in a voice channel?")


def setup(bot):
    bot.add_cog(Music(bot))
