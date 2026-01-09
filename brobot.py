import logging
import os
from datetime import datetime

import discord

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


@bot.listen()
async def on_connect():
    try:
        app_info = await bot.application_info()
        owner = app_info.owner
        # If the owner is a Team, use the team's owner user
        if isinstance(owner, discord.Team):
            owner = owner.owner
        if owner:
            await owner.send(f"{bot.user} connected at {datetime.now().isoformat()}")
            log.info(f"Sent connect DM to owner {owner}")
    except Exception as e:
        log.error(f"Failed to fetch application info: {e}")


bot.run(TOKEN)
