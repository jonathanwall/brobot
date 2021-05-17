import time

from discord import Embed
from discord.ext import commands


class ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """display the latency in milliseconds"""
        before = time.time()
        embed = Embed(title="Ping")
        message = await ctx.send(embed=embed)

        ping = (time.time() - before) * 1000
        embed.description = f"{int(ping)} ms"
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(ping(bot))
