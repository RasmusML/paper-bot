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

TEMPLATE_QUERIES_DIR = "queries/"
OUTPUT_PATH = "outputs/discord_bot_papers.json"

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def paperbot(ctx, query: str = None, date_since: str = None):
    """Fetch papers and send them to the channel."""
    if (query is None) or (date_since is None):
        return await ctx.send(HELP_INFO)

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    if query in template_queries:
        query = template_queries[query]

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        return await ctx.send("Invalid date format. Please use YYYY-MM-DD.")

    try:
        pb.fetch_papers(OUTPUT_PATH, query, since=since)
    except ValueError:
        return await ctx.send("Invalid query. Please check the syntax.")

    papers = pb.load_papers(OUTPUT_PATH)
    text = pb.format_paper_overview(papers, "discord")

    await ctx.send(text)


if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
