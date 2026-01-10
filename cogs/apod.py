import logging

import os
import re
import aiohttp
import discord
from datetime import datetime

log = logging.getLogger(__name__)

NASA_APOD_URL = "https://apod-api.sudos.site/v1/apod/"
API_KEY = os.environ.get("APOD_API_KEY")


def extract_youtube_id(url: str) -> str:
    """Extract YouTube video ID from various URL formats"""
    # Format: youtu.be/VIDEO_ID
    match = re.search(r"youtu\.be/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    # Format: youtube.com/watch?v=VIDEO_ID
    match = re.search(r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    # Format: youtube.com/embed/VIDEO_ID
    match = re.search(r"youtube\.com/embed/([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    return None


def convert_to_youtube_watch_url(url: str) -> str:
    """Convert any YouTube URL to the standard watch URL format"""
    video_id = extract_youtube_id(url)
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id}"
    return url


class APOD(discord.Cog):
    """NASA Astronomy Picture of the Day"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @discord.slash_command(name="apod")
    @discord.option(
        "date",
        description="Any date after June 16, 1995, in MM/DD/YYYY or YYYY-MM-DD format",
        required=False,
    )
    async def apod(self, ctx: discord.ApplicationContext, date: str = None):
        """Show NASA's Astronomy Picture of the Day"""
        await ctx.defer()

        if date is None:
            date = datetime.now()
        else:
            date_obj = None
            for fmt in ["%m/%d/%Y", "%Y-%m-%d"]:
                try:
                    date_obj = datetime.strptime(date, fmt)
                    break
                except ValueError:
                    continue

            if date_obj is None:
                embed = discord.Embed(
                    title="❌ Invalid Date Format",
                    description="Please use MM/DD/YYYY or YYYY-MM-DD format (e.g., 01/15/2024 or 2024-01-15)",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            first_apod_date = datetime(1995, 6, 16)
            if date_obj < first_apod_date:
                embed = discord.Embed(
                    title="❌ Date Too Early",
                    description="APOD pictures are only available from June 16, 1995 onwards.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            if date_obj > datetime.now():
                embed = discord.Embed(
                    title="❌ Date in the Future",
                    description="Please select a date that has already occurred.",
                    color=discord.Color.red(),
                )
                await ctx.respond(embed=embed, ephemeral=True)
                return

            date = date_obj

        date = date.strftime("%Y-%m-%d")

        async with aiohttp.ClientSession() as session:
            params = {"api_key": API_KEY, "date": date}

            async with session.get(NASA_APOD_URL, params=params) as response:
                if response.status != 200:
                    embed = discord.Embed(
                        title="❌ Error",
                        description="Failed to fetch the Astronomy Picture of the Day.",
                        color=discord.Color.red(),
                    )
                    await ctx.respond(embed=embed, ephemeral=True)
                    log.error(f"APOD API returned status {response.status}")
                    return

                data = await response.json()

        title = data.get("title", "Astronomy Picture of the Day")
        explanation = data.get("explanation", "No description available.")
        pic_date = data.get("date", "")
        url = data.get("url", "")
        media_type = data.get("media_type", "image")

        if len(explanation) > 4000:
            explanation = explanation[:3997] + "..."

        embed = discord.Embed(
            title=title,
            description=explanation,
            color=discord.Color.dark_blue(),
            url=url,
        )

        if media_type == "image":
            embed.set_image(url=url)
        elif media_type == "video":
            if "youtube.com" in url or "youtu.be" in url:
                video_id = extract_youtube_id(url)
                watch_url = convert_to_youtube_watch_url(url)
                if video_id:
                    thumbnail_url = (
                        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                    )
                    embed.set_image(url=thumbnail_url)
                    embed.add_field(
                        name="🎬 YouTube Video",
                        value=f"[Watch on YouTube]({watch_url})",
                        inline=False,
                    )
                else:
                    embed.add_field(
                        name="🎬 YouTube Video",
                        value=f"[Watch on YouTube]({watch_url})",
                        inline=False,
                    )
            else:
                embed.add_field(
                    name="🎬 Video",
                    value=f"[Watch Video]({url})",
                    inline=False,
                )

        embed.set_footer(text=f"📅 {pic_date} | NASA APOD")

        await ctx.respond(embed=embed)
        log.info(f"APOD fetched for {ctx.author} on {pic_date}: {title}")


def setup(bot: discord.Bot):
    bot.add_cog(APOD(bot))
