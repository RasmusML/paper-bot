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
- Example: `!paperbot "('machine learning' | 'ML') + 'AMP'" 2022-01-01`
"""

TEMPLATE_QUERIES_DIR = "queries/"
MAX_MESSAGE_LENGTH = 2_000

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def break_text(text: str, max_length: int) -> list[str]:
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def decompose_text(text: str, max_length: int) -> list[str]:
    texts = []

    lines = text.split("\n")

    text_builder = lines[0]
    for line in lines[1:]:
        if len(text_builder) > max_length:
            texts += break_text(text_builder, max_length)
            text_builder = ""
        elif len(text_builder) + len(line) > max_length:
            texts += [text_builder]
            text_builder = ""
        text_builder += "\n" + line

    texts += [text_builder]

    return texts


async def send(ctx, text):
    decomposed_text = decompose_text(text, MAX_MESSAGE_LENGTH)
    for text in decomposed_text:
        await ctx.send(text)


@bot.command()
async def paperbot(ctx, query: str = None, date_since: str = None):
    """Fetch papers and send them to the channel."""
    if (query is None) or (date_since is None):
        return await send(ctx, HELP_INFO)

    query = query.replace('"', "'")

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    if query in template_queries:
        query = template_queries[query]

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        return await send(ctx, "Invalid date format. Please use YYYY-MM-DD.")

    try:
        papers = pb.fetch_papers(query, since=since)
    except ValueError:
        return await send(ctx, "Invalid query. Please check the syntax.")

    papers = pb.prepare_papers(papers)
    text = pb.format_paper_overview(papers, since, "discord")

    await send(ctx, text)


if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
