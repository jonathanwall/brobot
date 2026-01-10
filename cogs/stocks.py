import asyncio
import logging

import discord
import yfinance as yf

log = logging.getLogger(__name__)


class Stocks(discord.Cog):
    """Get stock information"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="stocks")
    @discord.option(
        "ticker",
        description="Stock ticker symbol (e.g., AAPL, MSFT, GOOGL)",
        required=True,
    )
    async def stock(self, ctx: discord.ApplicationContext, ticker: str):
        """Get current stock price and information"""
        await ctx.defer()

        try:
            # Run yfinance in a thread to avoid blocking
            stock_data = await asyncio.to_thread(self._fetch_stock_data, ticker.upper())

            if stock_data is None:
                embed = discord.Embed(
                    title="❌ Stock Not Found",
                    description=f"Could not find data for '{ticker.upper()}'.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                log.warning(f"Stock not found: {ticker}")
                return

            current_price = stock_data.get("current_price")
            change = stock_data.get("change")
            change_percent = stock_data.get("change_percent")
            high_52w = stock_data.get("high_52w")
            low_52w = stock_data.get("low_52w")
            market_cap = stock_data.get("market_cap")
            pe_ratio = stock_data.get("pe_ratio")
            company_name = stock_data.get("company_name")

            if current_price is None:
                embed = discord.Embed(
                    title="❌ Unable to Fetch Data",
                    description=f"Could not retrieve data for '{ticker.upper()}'.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            color = discord.Color.green() if change >= 0 else discord.Color.red()
            change_indicator = "🟢" if change >= 0 else "🔴"

            embed = discord.Embed(
                title=f"📈 {ticker.upper()}",
                color=color,
            )

            if company_name:
                embed.description = company_name

            embed.add_field(
                name="Current Price",
                value=f"${current_price:,.2f}",
                inline=False,
            )

            embed.add_field(
                name="Price Change",
                value=f"{change_indicator} ${change:+,.2f} ({change_percent:+.2f}%)",
                inline=False,
            )

            if high_52w is not None and low_52w is not None:
                embed.add_field(
                    name="52 Week Range",
                    value=f"${low_52w:,.2f} - ${high_52w:,.2f}",
                    inline=True,
                )

            if market_cap is not None:
                if market_cap >= 1_000_000_000:
                    market_cap_str = f"${market_cap / 1_000_000_000:,.1f}B"
                elif market_cap >= 1_000_000:
                    market_cap_str = f"${market_cap / 1_000_000:,.1f}M"
                else:
                    market_cap_str = f"${market_cap:,.0f}"
                embed.add_field(
                    name="Market Cap",
                    value=market_cap_str,
                    inline=True,
                )

            if pe_ratio is not None and pe_ratio > 0:
                embed.add_field(
                    name="P/E Ratio",
                    value=f"{pe_ratio:.2f}",
                    inline=True,
                )

            await ctx.respond(embed=embed)
            log.info(f"Stock data fetched by {ctx.author} for {ticker.upper()}")

        except Exception as e:
            embed = discord.Embed(
                title="❌ Error",
                description=f"Failed to fetch stock data: {str(e)}",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            log.error(f"Error fetching stock data for {ticker}: {e}")

    def _fetch_stock_data(self, ticker: str) -> dict | None:
        """Fetch stock data from Yahoo Finance"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            # Check if we got valid data
            if not info or info.get("regularMarketPrice") is None:
                return None

            current_price = info.get("regularMarketPrice", 0)
            previous_close = info.get("regularMarketPreviousClose", 0)
            change = current_price - previous_close
            change_percent = (
                (change / previous_close * 100) if previous_close != 0 else 0
            )

            return {
                "current_price": current_price,
                "change": change,
                "change_percent": change_percent,
                "high_52w": info.get("fiftyTwoWeekHigh"),
                "low_52w": info.get("fiftyTwoWeekLow"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "company_name": info.get("longName"),
            }

        except Exception as e:
            log.error(f"Error fetching stock data for {ticker}: {e}")
            return None


def setup(bot: discord.Bot):
    bot.add_cog(Stocks(bot))
