import logging

import aiohttp
import discord

log = logging.getLogger(__name__)

COINGECKO_API_URL = "https://api.coingecko.com/api/v3/simple/price"


class Bitcoin(discord.Cog):
    """Get the current price of Bitcoin"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="bitcoin")
    @discord.option(
        "currency",
        description="Currency to display price in (USD, EUR, GBP, etc.)",
        default="USD",
    )
    async def bitcoin(self, ctx: discord.ApplicationContext, currency: str):
        """Get the current price of Bitcoin"""
        await ctx.defer()

        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    "ids": "bitcoin",
                    "vs_currencies": currency.lower(),
                    "include_24hr_change": "true",
                }

                async with session.get(COINGECKO_API_URL, params=params) as response:
                    if response.status != 200:
                        embed = discord.Embed(
                            title="❌ Error",
                            description=f"Failed to fetch Bitcoin price: {response.status}",
                            color=discord.Color.red(),
                        )
                        await ctx.respond(embed=embed, ephemeral=True)
                        log.error(f"CoinGecko API returned status {response.status}")
                        return

                    data = await response.json()

            bitcoin_data = data.get("bitcoin", {})
            currency_lower = currency.lower()
            price = bitcoin_data.get(currency_lower)

            if price is None:
                embed = discord.Embed(
                    title="❌ Invalid Currency",
                    description=f"Currency '{currency}' is not supported.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                log.warning(f"Invalid currency requested: {currency}")
                return

            change_24h = bitcoin_data.get(f"{currency_lower}_24h_change")

            embed = discord.Embed(
                title="₿ Bitcoin Price",
                color=discord.Color.orange(),
            )
            embed.add_field(
                name=f"Current Price",
                value=f"{currency.upper()} {price:,.2f}",
                inline=False,
            )

            if change_24h is not None:
                change_color = "🟢" if change_24h >= 0 else "🔴"
                embed.add_field(
                    name="24h Change",
                    value=f"{change_color} {change_24h:+.2f}%",
                    inline=True,
                )

            await ctx.respond(embed=embed)
            log.info(f"Bitcoin price fetched by {ctx.author} in {currency}")

        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to fetch Bitcoin price: {str(e)}",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            log.error(f"Error fetching Bitcoin price: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(Bitcoin(bot))
