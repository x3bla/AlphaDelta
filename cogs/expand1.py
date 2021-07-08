import discord
from discord.ext import commands
import random

class Example(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Expansion 1 is loaded")

    @commands.command(aliases=["8ball"])
    async def _8ball(self, ctx, *, question):
        responses = ["It is certain.",
                     "It is decidedly so.",
                     "Without a doubt.",
                     "Yes - definitely.",
                     "You may rely on it.",
                     "As I see it, yes.",
                     "Most likely.",
                     "Outlook good.",
                     "Yes.",
                     "Signs point to yes.",
                     "Reply hazy, try again.",
                     "Ask again later.",
                     "Better not tell you now.",
                     "Cannot predict now.",
                     "Don't count on it.",
                     "My reply is no.",
                     "My sources say no.",
                     "Outlook not so good.",
                     "Very doubtful.",
                     'For sure',
                     'Chances are low',
                     'Wouldn\'t count on it.',
                     'Nope',
                     'Try again',
                     'Think hard and try again',
                     'Go away before I eat your cat',
                     'I thought too hard and died.']
        await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")


def setup(bot):
    bot.add_cog(Example(bot))