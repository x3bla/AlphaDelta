import discord
from discord.ext import commands
import youtube_dl
import asyncio

youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {  # sets the quality of the audio
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # bind to ipv4 since ipv6 addresses cause issues sometimes
}

ffmpeg_options = {  # idk just don't delete
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)  # youtube download

client = commands.Bot(command_prefix='~')

# this is all copy paste from https://github.com/RK-Coding/Videos/blob/master/rkcodingmusicqueue.py
class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

# this is one hell of a library
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music is loaded")

    # commands starts here
    @commands.command()
    async def play(self, ctx, *, title):
        if ctx.author.voice is not None:
            channel = ctx.author.voice.channel  # finding which channel is the author
        else:
            await ctx.send("You're not in a voice channel")
            return

        await channel.connect()  # joining the channel itself

        server = ctx.message.guild
        voice_channel = server.voice_client

        async with ctx.typing():
            player = await YTDLSource.from_url(title, loop=client.loop)
            voice_channel.play(player, after=lambda e: print("Player error: %s' %e") if e else None)

        await ctx.send(f"**Now playing:** {player.title}")

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()
        await ctx.send("Bye!")


def setup(bot):
    bot.add_cog(Music(bot))
