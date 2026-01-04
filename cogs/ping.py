import time
import logging
import discord

log = logging.getLogger(__name__)


class Ping(discord.Cog):
    """Display the latency in milliseconds"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="ping")
    async def ping(self, ctx: discord.ApplicationContext):
        """Display the latency in milliseconds"""
        before = time.time()
        embed = discord.Embed(title="Pong")
        message = await ctx.send_response(embed=embed)

        ping = (time.time() - before) * 1000
        embed.description = f"{int(ping)} ms"
        await message.edit(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(Ping(bot))
