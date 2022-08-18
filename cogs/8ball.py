import random

import discord


class EightBall(discord.Cog):
    """Shakes a Magic 8 Ball"""

    def __init__(self, bot: discord.Bot):
        self.bot = bot
        self.image_url = (
            "https://user-images.githubusercontent.com/"
            + "642358/185277887-ea97cb17-85e3-4f45-971a-fc0f91edd38d.png"
        )

    @discord.slash_command(name="8ball")
    @discord.option("question", description="Ask a question", default="The Magic 8 Ball says...")
    async def eight_ball(self, ctx: discord.ApplicationContext, question: str):
        """Shake a Magic 8 Ball"""
        answers = (
            "As I see it, yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
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
            "Yes - definitely.",
            "You may rely on it.",
        )
        embed = discord.Embed(title=f"{question}")
        embed.description = f"**{random.choice(answers)}**"
        embed.set_thumbnail(url=self.image_url)
        await ctx.respond(embed=embed)


def setup(bot: discord.Bot):
    bot.add_cog(EightBall(bot))
