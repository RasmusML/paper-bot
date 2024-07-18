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

PAPERFIND_HELP_INFO = """
**Usage**
- Use `!paperfind <query> <date_since>` to fetch papers.
- Example: `!paperfind "('machine learning' | 'ML') + 'AMP'" 2022-01-01`
"""

PAPERLIKE_HELP_INFO = """
**Usage**
- Use `!paperlike <reference_paper_title>` to fetch similar papers.
- Example: `!paperlike "Attention is All You Need"`
"""

TEMPLATE_QUERIES_DIR = "queries/"

# Maximum number of papers to fetch
QUERY_PAPER_LIMIT = 100
TEMPLATE_QUERY_PAPER_LIMIT = 500
SIMILAR_PAPERS_LIMIT = 50

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


def break_text(text: str, max_length: int) -> list[str]:
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def break_text_with_newlines(text: str, max_length: int) -> list[str]:
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

    texts += break_text(text_builder, max_length)

    return texts


async def send(ctx, text):
    texts = break_text_with_newlines(text, max_length=2_000)

    # discord can not send whitespace messages
    texts = list(filter(lambda x: x.strip() != "", texts))

    for text in texts:
        await ctx.send(text)


@bot.command()  # type: ignore
async def paperfind(ctx, query: str = None, date_since: str = None):
    """Fetch papers and send them to the channel."""
    if (query is None) or (date_since is None):
        return await send(ctx, PAPERFIND_HELP_INFO)

    query_or_filename = query.replace('"', "'")

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    query = template_queries.get(query_or_filename, query_or_filename)
    limit = TEMPLATE_QUERY_PAPER_LIMIT if query_or_filename in template_queries else QUERY_PAPER_LIMIT

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        return await send(ctx, "Invalid date format. Please use YYYY-MM-DD.")

    try:
        papers = pb.fetch_papers_from_query(query, since=since, limit=limit)
    except ValueError:
        return await send(ctx, "Invalid query. Please check the syntax.")
    except RuntimeError:
        return await send(ctx, "Something went very wrong...")

    text = pb.format_query_papers(papers, since, "discord")

    await send(ctx, text)


@bot.command()  # type: ignore
async def paperlike(ctx, title: str = None):
    """Fetch similar papers and send them to the channel."""
    if title is None:
        return await send(ctx, PAPERLIKE_HELP_INFO)

    reference_paper, similar_papers = pb.fetch_similar_papers(title, limit=SIMILAR_PAPERS_LIMIT)
    text = pb.format_similar_papers(reference_paper, similar_papers, title, "discord")

    await send(ctx, text)


if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
