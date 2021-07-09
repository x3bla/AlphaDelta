from discord.ext import commands
import random

class Expand1(commands.Cog):

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
                     "Don't count on it.",
                     "My reply is no.",
                     "My sources say no.",
                     "Outlook not so good.",
                     "Very doubtful.",
                     'For sure',
                     'Chances are low',
                     'Wouldn\'t count on it.',
                     'Nope',
                     'Think hard and try again',
                     'Go away before I eat your cat',
                     'I thought too hard and died.']
        yesno = ["Yes", "No"]
        if "should" == question[:6].lower():
            await ctx.send(random.choice(yesno))
        else:
            await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")

    @_8ball.error
    async def _8ball_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("Please ask a question")


def setup(bot):
    bot.add_cog(Expand1(bot))
