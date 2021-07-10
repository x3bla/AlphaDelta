import json

from discord.ext import commands
import asyncio

def unloadJSON():
    with open("data.json", "r") as f:
        data = json.load(f)


def operators(ctx):
    return ctx.author.id == 807215269403426848


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
        print("Admin is loaded")

    @commands.command()
    @commands.has_any_role("Lord and savior", "Server Admin")
    async def purge(self, ctx, amount=5):
        await ctx.channel.purge(limit=amount)

    @commands.command()
    @commands.has_any_role("Lord and savior", "Server Admin")
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        await ctx.guild.kick(reason=reason)
        await ctx.send(f"{member} was yeeted.")

    @commands.command()
    @commands.has_any_role("Lord and savior", "Server Admin")
    async def ban(self, ctx, member: commands.MemberConverter, *, reason=None):
        await ctx.guild.ban(reason=reason)
        await ctx.send(f"{member} was yeeted^2.")

    @commands.command()
    @commands.has_any_role("Lord and savior", "Server Admin")
    async def tempban(self, ctx, member: commands.MemberConverter, duration: DurationConverter, *, reason=None):

        multiplier = {'s': 1, 'm': 60, 'h': 3600}
        amount, unit = duration

        await ctx.guild.ban(member, reason=reason)
        await ctx.send(f"{member} was yeeted^2 for {amount}{unit}.")
        await asyncio.sleep(amount * multiplier[unit])
        await ctx.guild.unban(member)

    @commands.command()
    @commands.has_any_role("Lord and savior", "Server Admin")
    async def unban(self, ctx, *, member):
        banned_users = await ctx.guild.bans()
        member_name, member_discriminator = member.split('#')

        for ban_entry in banned_users:
            user = ban_entry.user

            if (user.name, user.discriminator) == (member_name, member_discriminator):
                await ctx.guild.unban(user)
                await ctx.send(f"Unbanned {user.name}#{user.discriminator}")
                return


def setup(bot):
    bot.add_cog(Admin(bot))
