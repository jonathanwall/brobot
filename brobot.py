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

bot.run(TOKEN)
