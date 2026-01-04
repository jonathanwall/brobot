import logging

import discord

log = logging.getLogger(__name__)


class Latency(discord.Cog):
    """Display the latency in milliseconds"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="latency")
    async def latency(self, ctx: discord.ApplicationContext):
        """Display the latency in milliseconds"""
        await ctx.send_response(f"{self.bot.latency * 1000:.2f} ms", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Latency(bot))
