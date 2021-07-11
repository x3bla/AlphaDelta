import os
import discord
from discord.ext import commands, tasks
from itertools import cycle
import json
import traceback
import sys

# variables
headpatCache = 0
operator = []
token = ""

def unloadJSON():
    global operator
    global headpatCache
    global token
    with open("data.json", 'r') as f:
        data = json.load(f)
        headpatCache = data["headpats"]
        token = data["token"]
        operator = data["opID"]

def operators(ctx):
    global operator
    if ctx.author.id in operator:
        return True
    else:
        print(f"{ctx.author} attempted to perform a load action\n")
        return False

def saveHeadpats():
    with open("data.json", 'r') as f:
        data = json.load(f)
        data["headpats"] = headpatCache

    with open("data.json", 'w') as f:
        json.dump(data, f, indent = 2)


# giving points
def point():
    global headpatCache
    headpatCache += 1
    saveHeadpats()


# cycling through statuses
status = cycle(["8ball", "admin commands", "deciding life choices"])  # different statuses


# setting prefix and making commands case insensitive
bot = commands.Bot(command_prefix='~', case_insensitive=True)


# status changes
@tasks.loop(minutes=10)
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

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CheckFailure):
        print(f"{ctx.author} tried to use a command without proper perms")
        pass
    else:
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

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
    print(f"{ctx.author} has performed an admin action\n")

@bot.command()
@commands.check(operators)
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")
    print(f"{extension} has been unloaded\n")

@bot.command()
@commands.check(operators)
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")
    print(f"{extension} has been reloaded\n")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")


# main loop/run
unloadJSON()
bot.run(token)
