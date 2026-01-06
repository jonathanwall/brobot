import logging
import sqlite3
from datetime import datetime, timedelta
import re
import calendar
from pathlib import Path

import discord
from discord.commands import SlashCommandGroup
from discord.ext import commands, tasks

log = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent / "reminders.db"


def _add_months(dt: datetime, months: int) -> datetime:
    """Return dt + months, adjusting year and day overflow."""
    month = dt.month - 1 + months
    year = dt.year + month // 12
    month = month % 12 + 1
    day = min(dt.day, calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def parse_when_to_datetime(when: str) -> datetime:
    """Parse a flexible time description into a future datetime.

    Supports:
    - ISO: YYYY-MM-DD HH:MM or YYYY-MM-DD
    - US dates: MM/DD or MM/DD/YYYY (optional time)
    - Relative durations: "2h30m", "4h15", "30 minutes", "3 days", "in 2 weeks", "10 seconds"
    - Natural: "in a month", "in 1 year", "tomorrow", "today", "next week"
    - Weekday names: "monday", optionally with HH:MM
    """
    s = when.strip().lower()
    s = re.sub(r",", "", s)
    now = datetime.now()

    # Try ISO and common explicit formats
    explicit_formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%m/%d/%Y %H:%M",
        "%m/%d/%Y",
        "%m/%d %H:%M",
        "%m/%d",
    ]
    for fmt in explicit_formats:
        try:
            dt = datetime.strptime(s, fmt)
            # If format lacked year, fill with current year
            if fmt in ("%m/%d", "%m/%d %H:%M") and dt.year == 1900:
                dt = dt.replace(year=now.year)
            # If no time provided, default to 09:00
            if fmt in ("%Y-%m-%d", "%m/%d", "%m/%d/%Y"):
                dt = dt.replace(hour=9, minute=0)
            # If date-only and already passed, bump year
            if dt < now and fmt in ("%m/%d", "%m/%d/%Y", "%Y-%m-%d"):
                try:
                    dt = dt.replace(year=dt.year + 1)
                except Exception:
                    pass
            if dt < now:
                # For explicit datetimes, only accept future
                raise ValueError("Please specify a future date and time.")
            return dt
        except ValueError:
            continue

    # Natural keywords
    if s in ("now", "today"):
        return now
    if s == "tomorrow":
        return (now + timedelta(days=1)).replace(
            hour=9, minute=0, second=0, microsecond=0
        )
    if s == "next week":
        return (now + timedelta(weeks=1)).replace(
            hour=9, minute=0, second=0, microsecond=0
        )

    # Relative durations like 'in 2 weeks', '3 days', '30 minutes', 'in a month', '10 seconds'
    m = re.match(
        r"^(?:in\s+)?(?:(a|an)|([0-9]+))\s*(years?|yrs?|months?|weeks?|days?|hours?|hrs?|minutes?|mins?|m|seconds?|secs?|s)$",
        s,
    )
    if m:
        num = 1 if m.group(1) else int(m.group(2))
        unit = m.group(3)
        if unit.startswith("year") or unit.startswith("yr"):
            try:
                return now.replace(year=now.year + num)
            except Exception:
                # Feb 29 handling
                return now.replace(year=now.year + num, day=now.day - 1)
        if unit.startswith("month"):
            return _add_months(now, num)
        if unit.startswith("week"):
            return now + timedelta(weeks=num)
        if unit.startswith("day"):
            return now + timedelta(days=num)
        if unit.startswith("hour"):
            return now + timedelta(hours=num)
        if unit.startswith("min") or unit == "m":
            return now + timedelta(minutes=num)
        if unit.startswith("sec") or unit == "s":
            return now + timedelta(seconds=num)

    # Compact hour/min like '2h30m', '4h15', '2h', '30m'
    m = re.match(r"^(?:in\s+)?(?:(\d+)h(?:ours?)?)?(?:(\d+)m)?$", s)
    if m and (m.group(1) or m.group(2)):
        hours = int(m.group(1)) if m.group(1) else 0
        mins = int(m.group(2)) if m.group(2) else 0
        return now + timedelta(hours=hours, minutes=mins)

    # Weekday names optionally with time 'monday' or 'monday 14:30'
    days = [d.lower() for d in calendar.day_name]
    wd_match = re.match(
        r"^(?:next\s+)?(" + "|".join(days) + r")(?:\s+(\d{1,2}:\d{2}))?$", s
    )
    if wd_match:
        name = wd_match.group(1)
        timepart = wd_match.group(2)
        target_wd = days.index(name)
        days_ahead = (target_wd - now.weekday() + 7) % 7
        if days_ahead == 0:
            days_ahead = 7
        target = now + timedelta(days=days_ahead)
        if timepart:
            hh, mm = map(int, timepart.split(":"))
            target = target.replace(hour=hh, minute=mm, second=0, microsecond=0)
        else:
            target = target.replace(hour=9, minute=0, second=0, microsecond=0)
        return target

    raise ValueError(
        "Could not understand time. Examples: '2026-01-05 14:30', '12/3', 'in 2 weeks', '2h30m', 'monday 14:00'"
    )


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

    reminders = SlashCommandGroup("reminders", "Commands for managing reminders")

    @reminders.command(name="create")
    @discord.option(
        "text", description="What do you want to be reminded about?", required=True
    )
    @discord.option(
        "when",
        description="When? Understand formats like '2026-01-05 14:30', 'in 2 weeks', '2h30m', 'monday 14:00'",
        required=True,
    )
    async def reminders_create(
        self, ctx: discord.ApplicationContext, text: str, when: str
    ):
        """Add a reminder for a specific date and time"""
        try:
            reminder_dt = parse_when_to_datetime(when)
        except ValueError as exc:
            embed = discord.Embed(
                title="❌ Invalid Time Format",
                description=str(exc),
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

    @reminders.command(name="list")
    async def reminders_list(self, ctx: discord.ApplicationContext):
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

    @reminders.command(name="delete")
    @discord.option(
        "reminder_id", description="ID of the reminder to delete", required=True
    )
    async def reminders_delete(self, ctx: discord.ApplicationContext, reminder_id: int):
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

    @tasks.loop(seconds=1)
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
                    embed = discord.Embed(
                        title="🔔 Reminder",
                        description=text,
                        color=discord.Color.gold(),
                    )
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
