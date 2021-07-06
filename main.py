import discord
from discord.ext import commands
import random

# extra shit
intents = discord.Intents(messages = True, guilds = True, reactions = True, members = True, presences = True)
client = commands.Bot(command_prefix = '~', intents = intents)

@client.event
async def on_ready():
    print("Bot is ready.")

@client.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@client.event
async def on_member_remove(member):
    print(f'{member} has left a server')

@client.command()
async def alpha(ctx):
    await ctx.send("Delta!")

@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! \n{client.latency * 1000}ms")

@client.command(aliases=["8ball", "kms"])
async def _8ball(ctx, *, question):
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
                 "Concentrate and ask again.",
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

client.run('ODIzNDMxMTA4ODUwODc2NDY2.YFgt-g.QCRQDe7mLjoaOvJMn38kTcNu-jE')
