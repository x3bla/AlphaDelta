import os
import discord
from discord.ext import commands, tasks
from itertools import cycle

# giving points
def point():
    cache = int(points)
    cache += 1
    cache = str(cache)
    text = open("HeadPats.txt", "w")
    text.write(cache)
    text.close()
    cache = int(cache)

# declaring admins
def admin():
    admin_list = open("AdminList.txt")
    operators = admin_list.read()
    admin_list.close()

# locking certain commands
def authCheck(user):
    op_name, op_discriminator = operators.split('#') # note: might wanna make this take more operators
    if (user.name, user.discriminator) == (op_name, op_discriminator):
        print(f"{user.name}#{user.discriminator} has performed an admin action")
        return True
    else:
        return False


# variables
headpats = 0
operators = ""

# loading head pats
txt = open(r"HeadPats.txt")
points = int(txt.read())
txt.close()
status = cycle(["8ball", "admin commands", "deciding life choices"])   # different statuses

# setting prefix and making commands case insensitive
bot = commands.Bot(command_prefix='~', case_insensitive=True)


# status changes
@tasks.loop(hours=1)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))


# basic commands
@bot.event
async def on_ready():
    print("Bot is ready.")


@bot.event
async def on_member_join(member):
    print(f'{member} has joined a server.')


@bot.event
async def on_member_remove(member):
    print(f'{member} has left a server')


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


@bot.command()
async def load(ctx, extension):
    bot.load_extension(f"cogs.{extension}")


# loading/unloading listeners
@bot.command()
async def unload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    print(f"{extension} has been unloaded")


@bot.command()
async def reload(ctx, extension):
    bot.unload_extension(f"cogs.{extension}")
    bot.load_extension(f"cogs.{extension}")
    print(f"{extension} has been reloaded")

for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")

# main loop/run
admin()
Token = open(r"Token.txt")
bot.run(Token.read())
