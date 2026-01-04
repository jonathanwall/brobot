import logging
import random

import discord

log = logging.getLogger(__name__)


class Roll(discord.Cog):
    """Roll a variable sided die"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="roll")
    @discord.option("sides", description="Enter the number of sides", default=100)
    async def roll(self, ctx: discord.ApplicationContext, sides: int):
        """Roll a variable sided die"""
        embed = discord.Embed(title=f"Roll")
        embed.description = f"**{random.randint(1, sides)}**"
        embed.set_footer(text=f"(1 - {sides})")
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Roll(bot))
