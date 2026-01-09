import logging
import subprocess

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

log = logging.getLogger(__name__)


class System(discord.Cog):
    """Manage the server and system resources"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    system = SlashCommandGroup("system", "System management commands")

    @system.command(name="supervisor")
    @commands.is_owner()
    async def system_supervisor(self, ctx: discord.ApplicationContext):
        """Show supervisorctl status"""
        try:
            output = subprocess.getoutput("supervisorctl")

            # Truncate if output is too long for Discord embed
            if len(output) > 4096:
                output = output[:4090] + "..."

            embed = discord.Embed(
                description=f"```\n{output}\n```",
                color=discord.Color.blurple(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            log.info(f"Ran supervisorctl command for {ctx.author}")

        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"An error occurred: {str(e)}",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            log.error(f"Error running supervisorctl: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(System(bot))
