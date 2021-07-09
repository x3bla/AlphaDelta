import os
import discord
from discord.ext import commands, tasks
from itertools import cycle

# variables
headpatCache = 0

def operators(ctx):
    if ctx.author.id == 262505750922919937:
        return True
    elif ctx.author.id == 807215269403426848:
        return True
    else:
        print(f"{ctx.author} attempted to perform an admin action")
        return False

def saveToFIle():
    text = open("HeadPats.txt", "w")
    text.write(str(headpatCache))
    text.close()

def readFromFile():
    global headpatCache
    txt = open(r"HeadPats.txt")
    points = int(txt.read())
    txt.close()
    headpatCache = int(points)


# giving points
def point():
    global headpatCache
    headpatCache += 1
    saveToFIle()


# loading head pats
status = cycle(["8ball", "admin commands", "deciding life choices"])  # different statuses


# setting prefix and making commands case insensitive
bot = commands.Bot(command_prefix='~', case_insensitive=True)


# status changes
@tasks.loop(hours=1)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


# basic commands
@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(next(status)))
    print("Bot is ready.")

@bot.event
async def on_member_join(member):
    print(f'{member} has joined a server.')

@bot.event
async def on_member_remove(member):
    print(f'{member} has left a server')


#commands
@bot.command()
async def alpha(ctx):
    await ctx.send("Delta!")


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! \n{bot.latency * 1000}ms")


@bot.command()
async def goodBot(ctx):
    username = ctx.author.mention
    await ctx.send(f"Thanks {username} ヽ(=^･ω･^=)丿")
    point()
    print(headpatCache)


# loading/unloading listeners
@bot.command()
@commands.check(operators)
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")

@bot.command()
@commands.check(operators)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")
    print(f"{extension} has been unloaded")

@bot.command()
@commands.check(operators)
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")
    print(f"{extension} has been reloaded")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


# main loop/run
readFromFile()
Token = open(r"Token.txt")
bot.run(Token.read())
