import asyncio
import datetime
import json

import discord
from discord.ext import commands

# variables
opID = []
log_channel = {}

def unloadJSON():
    global opID
    global log_channel
    with open("data.json", "r") as f:
        data = json.load(f)
        opID = data["opID"]
        log_channel = data["log_channel"]

def saveJSON():
    global log_channel
    with open("data.json", "r") as f:
        data = json.load(f)
        data["log_channel"] = log_channel
    with open("data.json", 'w') as f:
        json.dump(data, f, indent=2)

def hasPerms(ctx):
    global opID
    if ctx.author.id in opID:
        return True
    elif ctx.message.author.guild_permissions.ban_members:
        return True
    else:
        try:
            return ctx.message.channel.permissions_for(ctx.author).ban_members
        except:
            print(f"{ctx.author} tried to use a command without proper perms")
            return False


class Admin(commands.Cog):

    class DurationConverter(commands.Converter):
        async def convert(self, ctx, argument):
            amount = argument[:-1]
            unit = argument[-1]

            if amount.isdigit() and unit in ['s', 'm', 'h']:
                return int(amount), unit

            raise commands.BadArgument(message="Not a valid duration")

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        unloadJSON()
        print("Admin is loaded")

    @commands.command()
    @commands.check(hasPerms)
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.check(hasPerms)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        print(self.bot.has_permissions)
        await member.kick(reason=reason)
        await ctx.send(f"{member} was yeeted.")

    @commands.command()
    @commands.check(hasPerms)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        await member.ban(reason=reason)
        await ctx.send(f"{member} was yeeted^2.")

    @commands.command()
    @commands.check(hasPerms)
    async def tempban(self, ctx, member: discord.Member, duration: DurationConverter, *, reason=None):

        multiplier = {'s': 1, 'm': 60, 'h': 3600}
        amount, unit = duration

        await member.ban(reason=reason)
        await ctx.send(f"{member} was yeeted^2 for {amount}{unit}.")
        await asyncio.sleep(amount * multiplier[unit])
        await ctx.guild.unban(member)

    @commands.command(aliases=["check"])
    @commands.check(hasPerms)
    async def check_bans(self, ctx):
        await ctx.message.delete()
        banned_users = [entry async for entry in ctx.guild.bans()]
        await ctx.send(banned_users, ephemeral=True, mention_author=True)

    @commands.command(aliases=["log"])
    @commands.check(hasPerms)
    async def log_channel(self, ctx, channel: discord.TextChannel):
        global log_channel

        await ctx.message.delete()
        log_channel[ctx.guild.id] = channel.id
        await channel.send("This channel is now being used for logging:"
                           "\n- Deleted comments\n- Edited comments\n- Reactions\n- Voice Channel Activity"
                           "\n\nNote: May not be able to detect messages prior to setting up this logger"
                           "\n-# To remove the logger, just delete the channel")

        with open("data.json", "r") as f:
            _data = json.load(f)
        _data["log_channel"][ctx.guild.id] = channel.id
        with open("data.json", "w") as f:
            json.dump(_data, f, indent=2)


    # log listeners
    @commands.Cog.listener("on_message")
    async def on_message(self, message):
        global log_channel

        if str(message.guild.id) not in log_channel:
            return
        if self.bot.get_channel(log_channel[str(message.guild.id)]) is None:
            log_channel.pop(str(message.guild.id))
            saveJSON()
            return
        if message.channel.id != log_channel[str(message.guild.id)]:
            return
        if message.author.bot and (message.author.id != self.bot.user.id):
            await message.delete()
            await message.channel.send(f"{message.author.mention} Get the fuck out you stupid bots", delete_after=3)

    @commands.Cog.listener("on_raw_message_delete")
    async def on_raw_message_delete(self, message):
        global log_channel
        msg = message.cached_message

        if str(message.guild_id) not in log_channel:
            return
        if self.bot.get_channel(log_channel[str(message.guild_id)]) is None:
            log_channel.pop(str(message.guild.id))
            saveJSON()
            return
        if msg is None:
            sec, milli_sec = str(datetime.datetime.now().timestamp()).split(".")
            await (self.bot.get_channel(log_channel[str(message.guild_id)])
               .send(f"<t:{sec}:F>.{milli_sec}: A message has been **deleted** in {self.bot.get_channel(message.channel_id).mention}"))
            return
        if msg.author.bot:
            return

        sec, milli_sec = str(msg.created_at.now().timestamp()).split(".")
        await (self.bot.get_channel(log_channel[str(msg.guild.id)])
               .send(f"<t:{sec}:F>.{milli_sec}: `{msg.author.display_name}`'s message has been **deleted**: "
                     f"`{msg.content}` in {self.bot.get_channel(message.channel_id).mention}"))

    @commands.Cog.listener("on_raw_message_edit")
    async def on_raw_message_edit(self, message):
        global log_channel
        msg = message.cached_message

        if str(message.guild_id) not in log_channel:
            return
        if self.bot.get_channel(log_channel[str(message.guild_id)]) is None:
            log_channel.pop(str(message.guild.id))
            saveJSON()
            return
        if message.message.author.bot:
            return

        if msg is None:  # if msg is not cached
            sec, milli_sec = str(datetime.datetime.now().timestamp()).split(".")
            await (self.bot.get_channel(log_channel[str(message.guild_id)])
                   .send(f"<t:{sec}:F>.{milli_sec}: `{message.message.author.display_name}` message has been **edited** to `{message.message.content}` "
                         f"at {message.message.jump_url}"))
            return

        sec, milli_sec = str(message.message.edited_at.timestamp()).split(".")
        await (self.bot.get_channel(log_channel[str(msg.guild.id)])
               .send(f"<t:{sec}:F>.{milli_sec}: `{msg.author.display_name}` has **edited** his message from "
                     f"`{msg.content}` to `{message.message.content}` at {message.message.jump_url}"))

    @commands.Cog.listener("on_voice_state_update")
    async def on_voice_state_update(self, member, before, after):
        global log_channel

        if str(member.guild.id) not in log_channel:
            return
        if self.bot.get_channel(log_channel[str(member.guild.id)]) is None:
            log_channel.pop(str(member.guild.id))
            saveJSON()
            return

        # if member.bot:  # to skip or not to skip bots hmm
        #     return

        msg = ""
        sec, mili_sec = str(datetime.datetime.now().timestamp()).split(".")

        # join channel
        if before.channel is None and  after.channel is not None:
            msg = f"<t:{sec}:F>.{mili_sec}: `{member.display_name}` has **connected** to {after.channel.jump_url}"

        # leave channel
        if after.channel is None and before.channel is not None:
            msg = f"<t:{sec}:F>.{mili_sec}: `{member.display_name}` has **disconnected** from {before.channel.jump_url}"

        # change channel
        if before.channel is not None and after.channel is not None and before.channel is not after.channel:
            msg = (f"<t:{sec}:F>.{mili_sec}: `{member.display_name}` has **changed** channel from {before.channel.jump_url}"
                   f"to {after.channel.jump_url}")

        if msg != "":
            await (self.bot.get_channel(log_channel[str(member.guild.id)]).send(msg))

    @commands.Cog.listener("on_raw_reaction_add")
    async def on_raw_reaction_add(self, member, before, after):
        global log_channel

        if str(member.guild.id) not in log_channel:
            return
        if self.bot.get_channel(log_channel[str(member.guild.id)]) is None:
            log_channel.pop(str(member.guild.id))
            saveJSON()
            return

        # if

    @commands.Cog.listener("on_raw_reaction_remove")
    async def on_raw_reaction_remove(self, member, before, after):
        global log_channel

        if str(member.guild.id) not in log_channel:
            return
        if self.bot.get_channel(log_channel[str(member.guild.id)]) is None:
            log_channel.pop(str(member.guild.id))
            saveJSON()
            return

        # if

async def setup(bot):
    unloadJSON()
    await bot.add_cog(Admin(bot))
