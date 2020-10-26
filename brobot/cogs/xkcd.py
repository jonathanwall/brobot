import aiohttp
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands


class xkcd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def xkcd(self, ctx):
        """ displays the latest xkcd comic """
        async with aiohttp.ClientSession() as session:
            async with session.get("http://xkcd.com") as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")
                title = soup.find("div", id="ctitle").contents[0]
                comic = soup.find(id="comic").find("img")
                embed = Embed(title=title, description=comic["title"], colour=0x002EFF)
                embed.set_image(url=f"https:{comic['src']}")
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(xkcd(bot))
