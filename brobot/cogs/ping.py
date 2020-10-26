import time

from discord.ext import commands


class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """ displays the latency in milliseconds """
        before = time.time()
        message = await ctx.send("ms")
        ping = (time.time() - before) * 1000
        await message.edit(content=f"`{int(ping)} ms`")


def setup(bot):
    bot.add_cog(ping(bot))
