from discord.ext import commands


class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    async def clear(self, ctx):
        await ctx.channel.purge()

    @clear.error
    async def clear_error(self, ctx, error):
        await ctx.send(error)


def setup(bot):
    bot.add_cog(clear(bot))
