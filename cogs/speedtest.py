from subprocess import PIPE, Popen

from discord import Embed
from discord.ext import commands


class speedtest(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def speedtest(self, ctx):
        """ speedtest """
        embed = Embed(title=f"Speedtest")
        embed.description = f"**running...(30s)**"
        message = await ctx.send(embed=embed)
        proc = Popen("/usr/local/bin/speedtest", shell=True, stdout=PIPE)
        outs, _ = proc.communicate(timeout=30)
        embed.description = f"{outs.decode('utf-8')}"
        await message.edit(embed=embed)


def setup(bot):
    bot.add_cog(speedtest(bot))
