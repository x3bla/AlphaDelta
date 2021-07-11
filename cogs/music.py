import discord
from discord.ext import commands, tasks
import youtube_dl

# gave up for now
class Music(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music is loaded")

    @commands.command()
    async def join(self, ctx):
        if ctx.author.voice is None:
            await ctx.send("You're not in a voice channel")
        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await voice_channel.connect

    @commands.command()
    async def leave(self, ctx):
        await ctx.voice_client.disconnect()


def setup(bot):
    bot.add_cog(Music(bot))
