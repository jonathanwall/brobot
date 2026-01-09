import logging
import os
import subprocess
import time
from datetime import datetime

import discord
from discord.ext import commands

TOKEN = os.environ["BROBOT_TOKEN"]
LOGLEVEL = os.environ.get("BROBOT_LOGLEVEL", "INFO").upper()

logging.basicConfig(
    level=LOGLEVEL,
    format="%(asctime)s %(levelname)-8s %(module)-s: %(funcName)s: %(message)s",
)

log = logging.getLogger(__name__)


class Brobot(discord.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_time = datetime.now()
        self.load_cogs_in_directory("cogs")

    def load_cogs_in_directory(self, directory: str):
        filepath = os.path.abspath(__file__)
        dirname = os.path.dirname(filepath) + f"/{directory}"

        if not os.path.isdir(dirname):
            log.warning(f"Cogs directory not found: {dirname}")
            return

        for filename in os.listdir(dirname):
            if filename.endswith(".py"):
                cog = f"{directory}." + filename.split(".")[0]
                try:
                    self.load_extension(cog)
                except Exception as e:
                    log.error(f"{cog} failed to load: {e}")
                else:
                    log.info(f"{cog} loaded")


description = "Brobot"
intents = discord.Intents.default()
bot = Brobot(description=description, intents=intents)


# Bot event listeners
@bot.listen()
async def on_connect():
    try:
        app_info = await bot.application_info()
        owner = app_info.owner
        # If the owner is a Team, use the team's owner user
        if isinstance(owner, discord.Team):
            owner = owner.owner
        if owner:
            await owner.send(f"{bot.user} connected")
            log.info(f"Sent connect DM to owner {owner}")
    except Exception as e:
        log.error(f"Failed to fetch application info: {e}")


# Bot command listeners
@bot.listen()
async def on_application_command(ctx: discord.ApplicationContext):
    log.info(f"Command '{ctx.command.name}' invoked by {ctx.author}")


@bot.listen()
async def on_application_command_completion(ctx: discord.ApplicationContext):
    log.info(f"Command '{ctx.command.name}' completed for {ctx.author}")


@bot.listen()
async def on_application_command_error(
    ctx: discord.ApplicationContext, error: Exception
):
    log.error(f"Error in command '{ctx.command.name}' invoked by {ctx.author}: {error}")


@bot.listen()
async def on_unknown_application_command(interaction: discord.Interaction):
    log.warning(f"Unknown command invoked by {interaction.user}")


# Bot commands
bot_group = bot.create_group("bot", "Commands for managing bot operations")


@bot_group.command(name="restart")
@commands.is_owner()
async def restart(ctx: discord.ApplicationContext):
    """Restart the bot"""
    embed = discord.Embed(
        title="✅ Restart",
        description=f"The bot is restarting",
        color=discord.Color.blurple(),
    )
    await ctx.respond(embed=embed, ephemeral=True)
    await bot.close()
    # Note: Actual restart logic (e.g., via a process manager) is not handled here.


@bot_group.command(name="update")
@commands.is_owner()
async def update(ctx: discord.ApplicationContext):
    """Update with the latest changes from the repository"""
    try:
        result = subprocess.run(
            ["git", "pull"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            embed = discord.Embed(
                title="✅ Update Successful",
                description=f"```{result.stdout}```",
                color=discord.Color.green(),
            )
        else:
            embed = discord.Embed(
                title="❌ Update Failed",
                description=f"```{result.stderr}```",
                color=discord.Color.red(),
            )
        await ctx.respond(embed=embed, ephemeral=True)
        log.info(f"Git pull executed by {ctx.author}: {result.returncode}")

    except Exception as e:
        embed = discord.Embed(
            title="❌ Update Error",
            description=f"```{str(e)}```",
            color=discord.Color.red(),
        )
        await ctx.respond(embed=embed, ephemeral=True)
        log.error(f"Git pull failed: {e}")


@bot_group.command(name="ping")
@commands.is_owner()
async def ping(ctx: discord.ApplicationContext):
    """Display the latency in milliseconds"""
    before = time.time()
    embed = discord.Embed(
        title="Ping", description="calculating...", color=discord.Color.blurple()
    )
    message = await ctx.send_response(embed=embed, ephemeral=True)

    ping = int((time.time() - before) * 1000)
    embed.description = f"{ping:.2f} ms"
    embed.color = discord.Color.green() if ping < 300 else discord.Color.red()
    await message.edit(embed=embed)


@bot_group.command(name="latency")
@commands.is_owner()
async def latency(ctx: discord.ApplicationContext):
    """Display the bot's latency in milliseconds"""
    latency = bot.latency * 1000
    color = discord.Color.green() if latency < 300 else discord.Color.red()
    embed = discord.Embed(
        title="Latency",
        description=f"{latency:.2f} ms",
        color=color,
    )
    await ctx.respond(embed=embed, ephemeral=True)


# Cogs commands
cogs_group = bot.create_group("cogs", "Commands for managing bot cogs")


@cogs_group.command(name="list")
@commands.is_owner()
async def list_cogs(ctx: discord.ApplicationContext):
    """List all loaded cogs"""
    loaded_cogs = list(bot.cogs)

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
            color=discord.Color.blurple(),
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
async def reload_cog(ctx: discord.ApplicationContext, cog: str):
    """Reload a specific cog"""
    try:
        bot.reload_extension(f"cogs.{cog.lower()}")
        embed = discord.Embed(
            description=f"Successfully reloaded `{cog}`",
            color=discord.Color.green(),
        )
        await bot.sync_commands()
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
async def unload_cog(ctx: discord.ApplicationContext, cog: str):
    """Unload a specific cog"""
    try:
        bot.unload_extension(f"cogs.{cog.lower()}")
        embed = discord.Embed(
            description=f"Successfully unloaded `{cog}`",
            color=discord.Color.green(),
        )
        await bot.sync_commands()
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
async def load_cog(ctx: discord.ApplicationContext, cog: str):
    """Load a cog"""
    try:
        bot.load_extension(f"cogs.{cog.lower()}")
        embed = discord.Embed(
            description=f"Successfully loaded `{cog}`",
            color=discord.Color.green(),
        )
        await bot.sync_commands()
        log.info(f"Loaded cog: {cog}")
    except Exception as e:
        embed = discord.Embed(
            title="Load Failed",
            description=f"Error loading `{cog}`: {e}",
            color=discord.Color.red(),
        )
        log.error(f"Failed to load cog {cog}: {e}")

    await ctx.respond(embed=embed, ephemeral=True)


bot.run(TOKEN)
