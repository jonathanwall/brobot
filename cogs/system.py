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

    @system.command(name="restart")
    @commands.is_owner()
    async def system_restart(self, ctx: discord.ApplicationContext):
        """Restart the bot"""
        await ctx.respond("Restarting bot...", ephemeral=True)
        await self.bot.close()

    @system.command(name="pull")
    @commands.is_owner()
    async def system_pull(self, ctx: discord.ApplicationContext):
        """Pull the latest changes from the repository"""
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                embed = discord.Embed(
                    title="✅ Git Pull Successful",
                    description=f"```{result.stdout}```",
                    color=discord.Color.green(),
                )
            else:
                embed = discord.Embed(
                    title="❌ Git Pull Failed",
                    description=f"```{result.stderr}```",
                    color=discord.Color.red(),
                )
            await ctx.respond(embed=embed, ephemeral=True)
            log.info(f"Git pull executed by {ctx.author}: {result.returncode}")

        except Exception as e:
            embed = discord.Embed(
                title="❌ Git Pull Error",
                description=f"```{str(e)}```",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            log.error(f"Git pull failed: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(System(bot))
