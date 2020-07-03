from discord.ext import commands


class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def clear(self, ctx):
        await ctx.channel.purge()


def setup(bot):
    bot.add_cog(clear(bot))
