from queue import Empty, Queue
from subprocess import PIPE, Popen
from threading import Thread
import asyncio

from discord import Embed
from discord.ext import commands


class speedtest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def speedtest(self, ctx):
        """speedtest"""
        embed = Embed(title=f"Speedtest")
        embed.description = f"**running...(30s)**"
        message = await ctx.send(embed=embed)
        proc = Popen("/usr/local/bin/speedtest", shell=True, stdout=PIPE)
        await asyncio.sleep(30)
        outs, _ = proc.communicate(timeout=0.1)
        outs = outs.decode("utf-8").splitlines()
        embed.description = f"**{outs[6]}\n{outs[8]}**"
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(speedtest(bot))
