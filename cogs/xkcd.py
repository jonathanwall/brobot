import aiohttp
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands


class xkcd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def xkcd(self, ctx):
        async with aiohttp.ClientSession() as session:
            async with session.get("http://xkcd.com") as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")
                title = soup.find("div", id="ctitle").contents[0]
                comic = soup.find(id="comic").find("img")
                em = Embed(title=title, description=comic["title"], colour=0x002EFF)
                em.set_image(url=f"https:{comic['src']}")
                em.set_author(name="xkcd.com", icon_url="https://xkcd.com/s/0b7742.png")
                await ctx.send(embed=em)

    @xkcd.error
    async def xkcd_error(self, ctx, error):
        await ctx.send(error)


def setup(bot):
    bot.add_cog(xkcd(bot))
