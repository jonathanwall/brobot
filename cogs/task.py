import logging
from discord.ext import commands, tasks

log = logging.getLogger(__name__)


class Task(commands.Cog):
    """A cog that demonstrates background tasks"""

    def __init__(self, bot):
        self.bot = bot
        self.index = 0
        self.printer.start()

    def cog_unload(self):
        self.printer.cancel()

    @tasks.loop(seconds=5)
    async def printer(self):
        log.debug(self.index)
        self.index += 1

    @printer.before_loop
    async def before_printer(self):
        await self.bot.wait_until_ready()


def setup(bot):
    try:
        bot.add_cog(Task(bot))
    except Exception as e:
        log.error(f"Failed to load Task cog: {e}")
