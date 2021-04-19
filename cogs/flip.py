import random

from discord import Embed
from discord.ext import commands


class flip(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def flip(self, ctx):
        """ flip a coin """
        embed = Embed(title="Flip")
        embed.description = f"**{random.choice(('heads', 'tails'))}**"
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(flip(bot))
