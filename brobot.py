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


bot.run(TOKEN)
