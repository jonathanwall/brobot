import random

from discord import Embed
from discord.ext import commands


class eight_ball(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="8ball")
    async def eight_ball(self, ctx, *, arg="8ball"):
        """shakes an 8ball"""
        answers = (
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don’t count on it.",
            "It is certain.",
            "It is decidedly so.",
            "Most likely.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Outlook good.",
            "Reply hazy, try again.",
            "Signs point to yes.",
            "Very doubtful.",
            "Without a doubt.",
            "Yes.",
            "Yes – definitely.",
            "You may rely on it.",
        )
        embed = Embed(title=f"{arg}")
        embed.description = f"**{random.choice(answers)}**"
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(eight_ball(bot))
