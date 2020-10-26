import os

import uvloop
from discord.ext import commands


def get_prefix(client, message):
    prefixes = [""]
    # prefix for DMs
    if not message.guild:
        prefixes = [""]
    # mention as prefix
    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    description="brobot",
    case_insensitive=True,
)


@bot.event
async def on_ready():
    # load all cogs in ./cogs
    filepath = os.path.abspath(__file__)
    cog_directory = os.path.dirname(filepath) + "/cogs"
    for filename in os.listdir(cog_directory):
        if filename.endswith(".py"):
            cog = "cogs." + filename.split(".", 1)[0]
            try:
                bot.load_extension(cog)
            except:
                continue


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    await ctx.send(error)


uvloop.install()
bot.run(os.getenv("discord_token"))
