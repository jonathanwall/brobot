import aiohttp
import feedparser
from bs4 import BeautifulSoup
from discord import Embed
from discord.ext import commands, tasks


class penny_arcade(commands.Cog):
    """ display the latest penny-arcade comic """

    def __init__(self, bot):
        self.bot = bot
        # self.feed_url = "https://xkcd.com/rss.xml"
        # self.etag = feedparser.parse(self.feed_url).etag
        # self.stream.start()

    async def get_embed(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                soup = BeautifulSoup(await resp.text(), "lxml")
                comic = soup.find(id="comicFrame").find("img")
                embed = Embed(title=comic["alt"])
                embed.set_image(url=comic["src"])
                return embed

    @commands.command(aliases=["penny-arcade"])
    async def penny_arcade(self, ctx):
        embed = await self.get_embed("https://www.penny-arcade.com/comic")
        await ctx.send(embed=embed)

    # async def get_embed(self, url):
    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(url) as resp:
    #             soup = BeautifulSoup(await resp.text(), "lxml")
    #             title = soup.find("div", id="ctitle").contents[0]
    #             comic = soup.find(id="comic").find("img")
    #             embed = Embed(title=title, description=comic["title"], colour=0x002EFF)
    #             embed.set_image(url=f"https:{comic['src']}")
    #             return embed

    # @tasks.loop(hours=1)
    # async def stream(self):
    #     feed = feedparser.parse(self.feed_url, etag=self.etag)
    #     if feed.status == 200:
    #         self.etag = feed.etag
    #         embed = await self.get_embed(feed.entries[0].id)
    #         info = await self.bot.application_info()
    #         owner = await self.bot.fetch_user(info.owner.id)
    #         await owner.send(embed=embed)

    # @commands.command()
    # async def xkcd(self, ctx):
    #     """ displays the latest comic from xkcd """
    #     embed = await self.get_embed("http://xkcd.com")
    #     await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(penny_arcade(bot))
