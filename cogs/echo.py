from discord.ext import commands


class echo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def echo(self, ctx, *, arg):
        """echo"""
        await ctx.send(arg)


def setup(bot):
    bot.add_cog(echo(bot))
