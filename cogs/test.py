import logging
import time

import discord

log = logging.getLogger(__name__)


class Test(discord.Cog):
    """Description for test cog"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="test")
    async def test(self, ctx: discord.ApplicationContext):
        """Description for test command"""
        embed = discord.Embed(title="Test")
        await ctx.send_response(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Test(bot))
