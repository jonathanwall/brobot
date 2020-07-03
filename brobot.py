import os

import uvloop
from discord.ext import commands


def get_prefix(client, message):
    prefixes = ["!"]

    if not message.guild:
        prefixes = ["!", ""]

    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(command_prefix=get_prefix, description="Brobot", case_insensitive=True,)


@bot.event
async def on_ready():
    filepath = os.path.abspath(__file__)
    dirname = os.path.dirname(filepath) + "/cogs"
    for filename in os.listdir(dirname):
        if filename.endswith(".py"):
            cog = "cogs." + filename.split(".", 1)[0]
            bot.load_extension(cog)


uvloop.install()
bot.run(os.getenv("discord_token"))
