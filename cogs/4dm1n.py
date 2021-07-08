import discord
from discord.ext import commands

class Example(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_ready(self):
        print("Admin is loaded")


    @commands.command()
    async def purge(self, ctx, amount=5):
        if authCheck() == True:
            await ctx.channel.purge(limit=amount)

    @commands.command()
    async def kick(self, ctx, member : discord.member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(f"{member}was yeeted.")


    @commands.command()
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
    bot.add_cog(Example(bot))