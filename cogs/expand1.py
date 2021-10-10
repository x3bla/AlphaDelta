from discord.ext import commands
import random

# lists
player2 = ["scissors", "paper", "stone"]
valid = ["scissors", "scissor", "paper", "stone", "rock"]
die = ["Pls no, I can do so much more", "Why have you brought my life to an end", "I still haven't had a family"]

# not safe
# def mathBreakUp(expression):
#     expression.replace("x", "*")
#     expression.replace("X", "*")
#     print(eval(expression))
#     return eval(expression)

def RPS_logic(p1, p2):
    if p1.lower() not in valid:
        return "bot"
    if p1.lower() == p2:
        return "both"
    if p1.lower() == "scissors" or "scissor":
        if p2 == "paper":
            return "player"
        else:
            return "bot"
    if p1.lower() == "paper":
        if p2 == "rock":
            return "player"
        else:
            return "bot"
    if p1.lower() == "stone" or "rock":
        if p2 == "scissors" or "scissor":
            return "player"
        else:
            return "bot"


class Expand1(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Expansion 1 is loaded")

    # commands starts here
    @commands.command()
    async def die(self, ctx):
        await ctx.send(random.choice(die))

    @commands.command(name="8ball", aliases=["8b"], help="I'll answer your yes or no question")
    async def _8ball(self, ctx, *, question):
        responses = ["It is certain.",      # the different responses
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

    # @commands.command(aliases=["cal"])      # 8x5/3+2-9
    # async def calculate(self, ctx, *, expression):
    #     await ctx.send(f"Question: {expression}\nAnswer: {mathBreakUp(expression)}")

    @commands.command(aliases=["RPS", "SPS"])
    async def rock_paper_scissors(self, ctx, player1):
        bot_choice = random.choice(player2)
        result = RPS_logic(player1, bot_choice)
        if result == "both":
            await ctx.send(f"{bot_choice}!\nI guess we tied.")
        elif result == "bot":
            await ctx.send(f"{bot_choice}!\nI win.")
        elif result == "player":
            await ctx.send(f"{bot_choice}!\nAwh I lost.")

    @commands.command()
    async def RandomNumber(self, range1, range2):
        RanNum = random.choice(range1, range2)
        await ctx.send(RanNum)


def setup(bot):
    bot.add_cog(Expand1(bot))
