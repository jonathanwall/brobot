import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path

import aiohttp
import discord
from discord.commands import SlashCommandGroup
from discord.ext import tasks

try:
    from zoneinfo import ZoneInfo
except Exception:
    ZoneInfo = None

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "apod.db"
NASA_API_KEY = os.environ.get("NASA_API_KEY", "DEMO_KEY")


class Apod(discord.Cog):
    """NASA APOD commands and daily scheduler.

    Commands (slash group `apod`):
    - `/apod now` : Fetch and show today's APOD
    - `/apod start` : Subscribe this channel to daily APOD at 8:00 AM Eastern
    - `/apod stop` : Unsubscribe this channel from daily APOD
    """

    def __init__(self, bot):
        self.bot = bot
        self.session = None
        self.init_db()

    async def cog_load(self):
        """Initialize session and start the daily task after cog is loaded."""
        self.session = aiohttp.ClientSession()
        self.daily_task.start()

    def cog_unload(self):
        self.daily_task.cancel()
        try:
            import asyncio

            if self.session:
                asyncio.create_task(self.session.close())
        except Exception:
            pass

    def init_db(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                channel_id INTEGER UNIQUE NOT NULL,
                last_sent_date TEXT
            )
            """
        )
        conn.commit()
        conn.close()

    async def fetch_apod(self):
        url = "https://api.nasa.gov/planetary/apod"
        params = {"api_key": NASA_API_KEY}
        try:
            async with self.session.get(url, params=params, timeout=20) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise RuntimeError(f"NASA API error: {resp.status} {text}")
                data = await resp.json()
                return data
        except Exception as e:
            log.error(f"Failed to fetch APOD: {e}")
            raise

    def build_apod_embed(self, data: dict) -> discord.Embed:
        title = data.get("title", "Astronomy Picture of the Day")
        explanation = data.get("explanation", "")
        url = data.get("url")
        hdurl = data.get("hdurl")
        copyright = data.get("copyright")

        embed = discord.Embed(title=title, description=explanation)
        if hdurl:
            embed.set_image(url=hdurl)
        elif url:
            embed.set_image(url=url)

        if copyright:
            embed.set_footer(text=f"© {copyright}")

        # If APOD is a video, include the URL and a note
        if data.get("media_type") == "video":
            embed.add_field(name="Media", value=f"Video: {url}")

        return embed

    async def send_apod_to_channel(self, channel_id: int):
        channel = self.bot.get_channel(channel_id)
        if channel is None:
            log.warning(f"Channel {channel_id} not found; removing subscription")
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM subscriptions WHERE channel_id = ?", (channel_id,))
            conn.commit()
            conn.close()
            return

        try:
            data = await self.fetch_apod()
            embed = self.build_apod_embed(data)
            await channel.send(embed=embed)
            log.info(f"Sent APOD to channel {channel_id}")
        except Exception as e:
            log.error(f"Error sending APOD to {channel_id}: {e}")

    apod = SlashCommandGroup("apod", "NASA APOD commands")

    @apod.command(name="now")
    async def apod_now(self, ctx: discord.ApplicationContext):
        """Show NASA's Astronomy Picture of the Day"""
        await ctx.defer()
        try:
            data = await self.fetch_apod()
            embed = self.build_apod_embed(data)
            await ctx.respond(embed=embed)
        except Exception:
            await ctx.respond("Failed to fetch APOD. Try again later.", ephemeral=True)

    @apod.command(name="start")
    async def apod_start(self, ctx: discord.ApplicationContext):
        """Subscribe this channel to daily APOD at 8:00 AM Eastern"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute(
            "INSERT OR IGNORE INTO subscriptions (channel_id, last_sent_date) VALUES (?, NULL)",
            (ctx.channel.id,),
        )
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ Subscribed",
            description="This channel will receive NASA's APOD every day at 8:00 AM Eastern.",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @apod.command(name="stop")
    async def apod_stop(self, ctx: discord.ApplicationContext):
        """Unsubscribe this channel from daily APOD"""
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("DELETE FROM subscriptions WHERE channel_id = ?", (ctx.channel.id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ Unsubscribed",
            description="This channel will no longer receive daily APOD posts.",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @tasks.loop(minutes=1)
    async def daily_task(self):
        # Compute current date/time in US/Eastern
        if ZoneInfo is None:
            # If zoneinfo not available, assume current local time; user may want to install backports
            now_local = datetime.now()
        else:
            try:
                eastern = ZoneInfo("America/New_York")
                now_local = datetime.now(tz=eastern)
            except Exception:
                now_local = datetime.now()

        # Check for 8:00 AM Eastern
        hour = now_local.hour
        minute = now_local.minute
        if not (hour == 8 and minute == 0):
            return

        today_str = now_local.date().isoformat()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT channel_id, last_sent_date FROM subscriptions")
        rows = c.fetchall()

        for channel_id, last_sent in rows:
            if last_sent == today_str:
                continue

            try:
                await self.send_apod_to_channel(channel_id)
                c.execute(
                    "UPDATE subscriptions SET last_sent_date = ? WHERE channel_id = ?",
                    (today_str, channel_id),
                )
                conn.commit()
            except Exception as e:
                log.error(f"Failed sending APOD to {channel_id}: {e}")

        conn.close()

    @daily_task.before_loop
    async def before_daily_task(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Apod(bot))
