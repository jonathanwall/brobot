import aiohttp
import feedparser
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands, tasks


class penny_arcade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["penny-arcade"])
    async def penny_arcade(self, ctx):
        """display the latest penny-arcade comic"""
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.penny-arcade.com/comic") as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")
                comic = soup.find(id="comicFrame").find("img")
                embed = Embed(title=comic["alt"])
                embed.set_image(url=comic["src"])
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(penny_arcade(bot))
