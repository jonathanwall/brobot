import logging
import sqlite3
import subprocess
import time
from pathlib import Path

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "settings.db"


class Settings(discord.Cog):
    """Manage the server and settings"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.init_db()

    def init_db(self):
        """Initialize the settings database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL
            )
        """
        )

    def get_setting(self, key: str) -> str:
        """Get a setting value by key"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def set_setting(self, key: str, value: str) -> bool:
        """Set a setting value by key"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )
            conn.commit()
            conn.close()
            log.info(f"Setting {key} updated to {value}")
            return True
        except Exception as e:
            log.error(f"Failed to set setting {key}: {e}")
            return False

    settings = SlashCommandGroup("settings", "Settings management commands")
    bot = settings.create_subgroup("bot", "Bot management commands")

    @bot.command(name="restart")
    @commands.is_owner()
    async def settings_bot_restart(self, ctx: discord.ApplicationContext):
        """Restart the bot"""
        await ctx.respond("Restarting bot...", ephemeral=True)
        await self.bot.close()

    @bot.command(name="update")
    @commands.is_owner()
    async def settings_bot_update(self, ctx: discord.ApplicationContext):
        """Update with the latest changes from the repository"""
        try:
            result = subprocess.run(
                ["git", "pull"],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                embed = discord.Embed(
                    title="✅ Update Successful",
                    description=f"```{result.stdout}```",
                    color=discord.Color.green(),
                )
            else:
                embed = discord.Embed(
                    title="❌ Update Failed",
                    description=f"```{result.stderr}```",
                    color=discord.Color.red(),
                )
            await ctx.respond(embed=embed, ephemeral=True)
            log.info(f"Git pull executed by {ctx.author}: {result.returncode}")

        except Exception as e:
            embed = discord.Embed(
                title="❌ Update Error",
                description=f"```{str(e)}```",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            log.error(f"Git pull failed: {e}")

    @bot.command(name="ping")
    @commands.is_owner()
    async def settings_bot_ping(self, ctx: discord.ApplicationContext):
        """Display the latency in milliseconds"""
        before = time.time()
        embed = discord.Embed(
            title="Ping", description="calculating...", color=discord.Color.blue()
        )
        message = await ctx.send_response(embed=embed, ephemeral=True)

        ping = (time.time() - before) * 1000
        embed.description = f"{int(ping)} ms"
        embed.color = discord.Color.green() if ping < 300 else discord.Color.red()
        await message.edit(embed=embed)

    @bot.command(name="latency")
    @commands.is_owner()
    async def settings_bot_latency(self, ctx: discord.ApplicationContext):
        """Display the latency in milliseconds"""
        await ctx.send_response(f"{self.bot.latency * 1000:.2f} ms", ephemeral=True)


def setup(bot: discord.Bot):
    bot.add_cog(Settings(bot))
