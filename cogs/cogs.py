import logging
import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

log = logging.getLogger(__name__)


class Cogs(discord.Cog):
    """Manage bot cogs (extensions)"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    cogs_group = SlashCommandGroup("cogs", "Commands for managing bot cogs")

    @cogs_group.command(name="list")
    @commands.is_owner()
    async def list_cogs(self, ctx: discord.ApplicationContext):
        """List all loaded cogs"""
        loaded_cogs = list(self.bot.cogs)

        if not loaded_cogs:
            embed = discord.Embed(
                title="Loaded Cogs",
                description="No cogs are currently loaded.",
                color=discord.Color.red(),
            )
        else:
            embed = discord.Embed(
                title="Loaded Cogs",
                description="\n".join(f"• {cog}" for cog in sorted(loaded_cogs)),
                color=discord.Color.green(),
            )
            embed.set_footer(text=f"Total: {len(loaded_cogs)} cogs")

        await ctx.respond(embed=embed, ephemeral=True)

    @cogs_group.command(name="reload")
    @commands.is_owner()
    @discord.option(
        "cog",
        description="The name of the cog to reload",
        required=True,
        autocomplete=discord.utils.basic_autocomplete(lambda ctx: list(ctx.bot.cogs)),
    )
    async def reload_cog(self, ctx: discord.ApplicationContext, cog: str):
        """Reload a specific cog"""
        try:
            self.bot.reload_extension(f"cogs.{cog.lower()}")
            embed = discord.Embed(
                description=f"Successfully reloaded `{cog}`",
                color=discord.Color.green(),
            )
            await self.bot.sync_commands()
            log.info(f"Reloaded cog: {cog}")
        except Exception as e:
            embed = discord.Embed(
                title="Reload Failed",
                description=f"Error reloading `{cog}`: {e}",
                color=discord.Color.red(),
            )
            log.error(f"Failed to reload cog {cog}: {e}")

        await ctx.respond(embed=embed, ephemeral=True)

    @cogs_group.command(name="unload")
    @commands.is_owner()
    @discord.option(
        "cog",
        description="The name of the cog to unload",
        required=True,
        autocomplete=discord.utils.basic_autocomplete(lambda ctx: list(ctx.bot.cogs)),
    )
    async def unload_cog(self, ctx: discord.ApplicationContext, cog: str):
        """Unload a specific cog"""
        try:
            self.bot.unload_extension(f"cogs.{cog.lower()}")
            embed = discord.Embed(
                description=f"Successfully unloaded `{cog}`",
                color=discord.Color.green(),
            )
            await self.bot.sync_commands()
            log.info(f"Unloaded cog: {cog}")
        except Exception as e:
            embed = discord.Embed(
                title="Unload Failed",
                description=f"Error unloading `{cog}`: {e}",
                color=discord.Color.red(),
            )
            log.error(f"Failed to unload cog {cog}: {e}")

        await ctx.respond(embed=embed, ephemeral=True)

    @cogs_group.command(name="load")
    @commands.is_owner()
    @discord.option("cog", description="The name of the cog to load", required=True)
    async def load_cog(self, ctx: discord.ApplicationContext, cog: str):
        """Load a cog"""
        try:
            self.bot.load_extension(f"cogs.{cog.lower()}")
            embed = discord.Embed(
                description=f"Successfully loaded `{cog}`",
                color=discord.Color.green(),
            )
            await self.bot.sync_commands()
            log.info(f"Loaded cog: {cog}")
        except Exception as e:
            embed = discord.Embed(
                title="Load Failed",
                description=f"Error loading `{cog}`: {e}",
                color=discord.Color.red(),
            )
            log.error(f"Failed to load cog {cog}: {e}")

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Cogs(bot))
