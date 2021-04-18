import random

from discord import Embed
from discord.ext import commands


class roll(commands.Cog):
    """ roll a variable sided die """

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, arg=100):
        """ roll a variable sided die """
        embed = Embed(title=f"Roll")
        embed.description = f"**{random.randint(1, int(arg))}**"
        embed.set_footer(text=f"(1 - {arg})")
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(roll(bot))
