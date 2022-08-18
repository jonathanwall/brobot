import logging
import os
from datetime import datetime

import discord

TOKEN = os.getenv("discord_token")
LOGLEVEL = os.environ.get("BB_LOGLEVEL", "ERROR").upper()

logging.basicConfig(
    level=LOGLEVEL,
    format="%(asctime)s %(levelname)s %(module)s: %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
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

        for filename in os.listdir(dirname):
            if filename.endswith(".py"):
                cog = f"{directory}." + filename.split(".")[0]
                try:
                    self.load_extension(cog)
                except:
                    pass
                else:
                    log.info(f"{cog} loaded")


description = "Brobot"
intents = discord.Intents.default()
bot = Brobot(description=description, intents=intents)


@bot.event
async def on_connect():
    log.debug("on_connect")


@bot.event
async def on_disconnect():
    log.debug("on_disconnect")


@bot.event
async def on_ready():
    log.debug("on_ready")


@bot.event
async def on_resumed():
    log.debug("on_resumed")


# @bot.event
# async def on_error(event: str, *args, **kwargs):
#     log.debug("on_error")
#     discord.on_error(event, *args, **kwargs)


# @bot.command()
# async def uptime(ctx: discord.ApplicationContext):
#     """Displays the uptime"""
#     uptime = datetime.now() - bot.start_time
#     embed = discord.Embed(title="Uptime", description=f"{uptime}")
#     await ctx.respond(embed=embed)


bot.run(TOKEN)
