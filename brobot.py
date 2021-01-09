import logging
import os
from datetime import datetime

import uvloop
from discord import Embed
from discord.ext import commands


def get_prefix(client, message):
    prefixes = [""]

    if not message.guild:
        prefixes = [""]

    return commands.when_mentioned_or(*prefixes)(client, message)


bot = commands.Bot(
    command_prefix=get_prefix,
    description="Brobot",
    case_insensitive=True,
)


async def load_all_cogs():
    filepath = os.path.abspath(__file__)
    dirname = os.path.dirname(filepath) + "/cogs"

    for filename in os.listdir(dirname):
        if filename.endswith(".py"):
            cog = "cogs." + filename.split(".")[0]
            try:
                bot.load_extension(cog)
            except:
                pass


@bot.event
async def on_ready():
    await load_all_cogs()


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.errors.CommandNotFound):
        return
    await ctx.send(error)


@bot.command()
async def uptime(ctx):
    """ displays the bot's uptime """
    uptime = datetime.now() - start_time
    embed = Embed(title="Uptime", description=f"{uptime}")
    await ctx.send(embed=embed)


@bot.command()
async def cogs(ctx):
    """ displays the bot's loaded cogs """
    cogs = ""
    for cog in bot.cogs:
        cog = bot.get_cog(cog)
        cogs += f"{cog.qualified_name} - {cog.description}\n"
    embed = Embed(title="Cogs", description=cogs)
    await ctx.send(embed=embed)


@bot.command(aliases=["exts"])
async def extensions(ctx):
    """ displays the bot's loaded extensions """
    exts = ""
    for ext in bot.extensions:
        exts += f"{ext}\n"
    embed = Embed(title="Extensions", description=exts)
    await ctx.send(embed=embed)


@bot.command()
async def remove_cog(ctx, arg):
    """ remove the specified cog """
    cog = bot.get_cog(arg)
    if cog is not None:
        bot.remove_cog(arg)
        await ctx.send(f"{arg} removed")
    else:
        await ctx.send(f"{arg} not found")


@bot.command()
async def unload_extension(ctx, arg):
    """ unload the specified extension """
    try:
        bot.unload_extension(arg)
    except commands.ExtensionNotLoaded:
        await ctx.send(f"{arg} not loaded")
    else:
        await ctx.send(f"{arg} unloaded")


@bot.command()
async def load_extension(ctx, arg):
    """ load the specified extension """
    try:
        bot.load_extension(arg)
    except commands.ExtensionNotFound:
        await ctx.send(f"{arg} not found")
    except commands.ExtensionAlreadyLoaded:
        await ctx.send(f"{arg} already loaded")
    except commands.NoEntryPointError:
        await ctx.send(f"{arg} has no entry point")
    except commands.ExtensionFailed:
        await ctx.send(f"{arg} has failed to load")
    else:
        await ctx.send(f"{arg} loaded")


@bot.command()
async def reload_extension(ctx, arg):
    """ remove the specified extension """
    try:
        bot.reload_extension(arg)
    except commands.ExtensionNotLoaded:
        await ctx.send(f"{arg} not loaded")
    except commands.ExtensionNotFound:
        await ctx.send(f"{arg} not found")
    except commands.NoEntryPointError:
        await ctx.send(f"{arg} has no entry point")
    except commands.ExtensionFailed:
        await ctx.send(f"{arg} has failed to load")
    else:
        await ctx.send(f"{arg} reloaded")


uvloop.install()
start_time = datetime.now()
bot.run(os.getenv("discord_token"))