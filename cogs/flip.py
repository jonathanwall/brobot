import logging
import random

import discord

log = logging.getLogger(__name__)


class Flip(discord.Cog):
    """Flip a coin"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="flip")
    @discord.option(
        "times",
        description="Number of times to flip",
        min_value=1,
        max_value=100,
        default=1,
    )
    async def flip(self, ctx: discord.ApplicationContext, times: int):
        """Flip a 2-sided coin"""
        embed = discord.Embed(title="Flip")
        embed.description = ""
        for _ in range(times):
            embed.description += f"**{random.choice(('Heads', 'Tails'))}**\n"
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Flip(bot))


# heads = "https://user-images.githubusercontent.com/642358/185279984-c516913b-9335-41ff-a2eb-70cb4a153582.png"
# tails = "https://user-images.githubusercontent.com/642358/185281016-4b206374-6b4f-412a-b829-70eb16ca4cf8.png"
