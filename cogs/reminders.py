import logging
import sqlite3
from datetime import datetime
from pathlib import Path

import discord
from discord.ext import commands, tasks

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "reminders.db"


class Reminders(commands.Cog):
    """Manage reminders that notify you at specific times"""

    def __init__(self, bot):
        self.bot = bot
        self.init_db()
        self.check_reminders.start()

    def cog_unload(self):
        self.check_reminders.cancel()

    def init_db(self):
        """Initialize the reminders database"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                channel_id INTEGER NOT NULL,
                reminder_text TEXT NOT NULL,
                reminder_time TEXT NOT NULL,
                created_at TEXT NOT NULL,
                sent INTEGER DEFAULT 0
            )
        """
        )
        conn.commit()
        conn.close()

    @discord.slash_command(name="remind")
    @discord.option(
        "text", description="What do you want to be reminded about?", required=True
    )
    @discord.option(
        "when",
        description="When? Format: YYYY-MM-DD HH:MM (e.g., 2025-01-05 14:30)",
        required=True,
    )
    async def remind(self, ctx: discord.ApplicationContext, text: str, when: str):
        """Add a reminder for a specific date and time"""
        try:
            reminder_dt = datetime.strptime(when, "%Y-%m-%d %H:%M")
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Time Format",
                description="Please use format: `YYYY-MM-DD HH:MM`\nExample: `2025-01-05 14:30`",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        if reminder_dt < datetime.now():
            embed = discord.Embed(
                title="❌ Time in the Past",
                description="Please specify a future date and time.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO reminders (user_id, channel_id, reminder_text, reminder_time, created_at)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                ctx.author.id,
                ctx.channel.id,
                text,
                reminder_dt.isoformat(),
                datetime.now().isoformat(),
            ),
        )
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ Reminder Set",
            description=f"You'll be reminded on **{reminder_dt.strftime('%Y-%m-%d at %H:%M')}**",
            color=discord.Color.green(),
        )
        embed.add_field(name="Reminder", value=f"_{text}_", inline=False)
        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="reminders")
    async def list_reminders(self, ctx: discord.ApplicationContext):
        """View all your active reminders"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, reminder_text, reminder_time FROM reminders WHERE user_id = ? AND sent = 0 ORDER BY reminder_time ASC",
            (ctx.author.id,),
        )
        reminders = cursor.fetchall()
        conn.close()

        if not reminders:
            embed = discord.Embed(
                title="No Active Reminders",
                description="You don't have any upcoming reminders.",
                color=discord.Color.blurple(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            return

        embed = discord.Embed(
            title="Your Reminders",
            color=discord.Color.blurple(),
        )
        for reminder_id, text, time_str in reminders:
            reminder_dt = datetime.fromisoformat(time_str)
            embed.add_field(
                name=f"ID: {reminder_id}",
                value=f"{text}\n🕐 {reminder_dt.strftime('%Y-%m-%d at %H:%M')}",
                inline=False,
            )

        await ctx.respond(embed=embed, ephemeral=True)

    @discord.slash_command(name="delete_reminder")
    @discord.option(
        "reminder_id", description="ID of the reminder to delete", required=True
    )
    async def delete_reminder(self, ctx: discord.ApplicationContext, reminder_id: int):
        """Delete a reminder"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id FROM reminders WHERE id = ?",
            (reminder_id,),
        )
        result = cursor.fetchone()

        if not result:
            embed = discord.Embed(
                title="❌ Reminder Not Found",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            conn.close()
            return

        if result[0] != ctx.author.id:
            embed = discord.Embed(
                title="❌ Not Your Reminder",
                description="You can only delete your own reminders.",
                color=discord.Color.red(),
            )
            await ctx.respond(embed=embed, ephemeral=True)
            conn.close()
            return

        cursor.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        conn.commit()
        conn.close()

        embed = discord.Embed(
            title="✅ Reminder Deleted",
            color=discord.Color.green(),
        )
        await ctx.respond(embed=embed, ephemeral=True)

    @tasks.loop(seconds=10)
    async def check_reminders(self):
        """Check for reminders that need to be sent"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        now = datetime.now()

        cursor.execute(
            """
            SELECT id, user_id, channel_id, reminder_text, reminder_time
            FROM reminders
            WHERE sent = 0 AND reminder_time <= ?
            ORDER BY reminder_time ASC
        """,
            (now.isoformat(),),
        )
        due_reminders = cursor.fetchall()

        for reminder_id, user_id, channel_id, text, reminder_time in due_reminders:
            try:
                channel = self.bot.get_channel(channel_id)
                if channel:
                    user = await self.bot.fetch_user(user_id)
                    embed = discord.Embed(
                        title="🔔 Reminder",
                        description=text,
                        color=discord.Color.gold(),
                    )
                    embed.set_footer(text=f"Reminder for {user.name}")
                    await channel.send(f"<@{user_id}>", embed=embed)
                    log.info(f"Sent reminder {reminder_id} to {user_id}")
            except Exception as e:
                log.error(f"Failed to send reminder {reminder_id}: {e}")

            cursor.execute("UPDATE reminders SET sent = 1 WHERE id = ?", (reminder_id,))

        conn.commit()
        conn.close()

    @check_reminders.before_loop
    async def before_check_reminders(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(Reminders(bot))
