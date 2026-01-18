from discord.ext import commands
import random


# lists
die = ["Pls no, I can do so much more", "Why have you brought my life to an end", "I still haven't had a family"]
rps = ["rock", "stone", "paper", "cloth", "scissor", "scissors"]
with open("MindBreak.txt", "r") as f:
    mindBreak = f.readlines()
    # print(mindBreak)

# not safe
# def mathBreakUp(expression):
#     expression.replace("x", "*")
#     expression.replace("X", "*")
#     print(eval(expression))
#     return eval(expression)

def RPS_logic(p1, bot):
    if p1 not in rps:
        return False
    if p1.lower() == "rock" or p1.lower() == "stone":  # changing string to int to prevent spam
        p1 = 1
    elif p1.lower() == "paper" or p1.lower() == "cloth":
        p1 = 2
    elif p1.lower() == "scissor" or p1.lower() == "scissors":
        p1 = 3
    if p1 == bot:
        return "both"

    if p1 == 3:  # scissors
        if bot == 2:  # paper
            return "player"  # 1=rock 2=paper 3=scissors
        else:
            return "bot"
    if p1 == 2:  # paper
        if bot == 1:  # rock
            return "player"
        else:
            return "bot"
    if p1 == 2:  # paper
        if bot == 3:  # scissors
            return "player"
        else:
            return "bot"


class Misc1(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Misc 1 is loaded")

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

        bot_choice = random.randint(1, 3)
        result = RPS_logic(player1, bot_choice)

        if bot_choice == 1:  # changing number to string
            bot_choice_str = "Rock"
        elif bot_choice == 2:
            bot_choice_str = "Paper"
        else:
            bot_choice_str = "Scissors"

        if result == "both":
            await ctx.send(f"{bot_choice_str}!\nI guess we tied.")
        elif result == "bot":
            await ctx.send(f"{bot_choice_str}!\nI win.")
        elif result == "player":
            await ctx.send(f"{bot_choice_str}!\nAwh I lost.")

    @commands.command(aliases=["RNG", "rn", "randomnum"])
    async def RandomNumber(self, ctx, range1, range2):
        RanNum = random.randint(int(range1), int(range2))
        await ctx.send(RanNum)

    @commands.command(aliases=["uhh", "dumb"])
    async def MindBreak(self, ctx):
        await ctx.send(random.choice(mindBreak))


async def setup(bot):
    await bot.add_cog(Misc1(bot))
