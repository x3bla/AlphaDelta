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


def unload_json():
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


def save_headpats():
    with open("data.json", 'r') as f:
        data = json.load(f)
        data["headpats"] = headpatCache
    with open("data.json", 'w') as f:
        json.dump(data, f, indent=2)


# giving points
def point():
    global headpatCache
    headpatCache += 1
    save_headpats()

def load(name):
    bot.load_extension(name)


# cycling through statuses
status = cycle(["8ball", "Jamming to youtube", "deciding life choices"])  # different statuses

# setting prefix and making commands case-insensitive
# setting up intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', case_insensitive=True, intents=intents)


# status changes
@tasks.loop(minutes=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


# basic commands
@bot.event
async def on_ready():
    change_status.start()
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")

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


# commands
@bot.command()
async def alpha(ctx):
    await ctx.send("Delta!")


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! \n{bot.latency * 1000}ms")


@bot.command(aliases=["headpat", "headpet", "pet"])
async def good_bot(ctx):
    username = ctx.author.mention
    await ctx.send(f"Thanks {username} ヽ(=^･ω･^=)丿")
    point()
    print(headpatCache)


# loading/unloading listeners
@bot.command()
@commands.check(operators)
async def load(ctx, extension):
    await bot.load_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action\n")


@bot.command()
@commands.check(operators)
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")
    print(f"{extension} has been unloaded\n")


@bot.command()
@commands.check(operators)
async def reload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await bot.load_extension(f"cogs.{extension}")
    print(f"{ctx.author} has performed an admin action")
    print(f"{extension} has been reloaded\n")


# main loop/run
unload_json()
bot.run(token)

