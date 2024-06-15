"""Script to run a Discord bot that fetches scientific papers.

References
----------
- https://discordpy.readthedocs.io/en/latest/discord.html
- https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html

"""

import datetime
import logging
import os

import discord
import paperbot as pb
from discord.ext import commands
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

HELP_INFO = """
**PaperBot Usage**
- Use `!paperbot <query> <date_since>` to fetch papers.
- Example: `!paperbot "([machine learning] OR [ML]) AND [AMP]" 2022-01-01`
"""


load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def paperbot(ctx, query: str = None, date_since: str = None):
    """Fetch papers and send them to the channel."""
    output_path = "outputs/discord_bot_papers.json"

    if (query is None) or (date_since is None):
        return await ctx.send(HELP_INFO)

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        return await ctx.send("Invalid date format. Please use YYYY-MM-DD.")

    pb.fetch_papers(output_path, query, since=since)

    papers = pb.load_papers(output_path)
    text = pb.format_paper_overview(papers, "discord")

    await ctx.send(text)


if __name__ == "__main__":
    BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
    bot.run(BOT_TOKEN)
