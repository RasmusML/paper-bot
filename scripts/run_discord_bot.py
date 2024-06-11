import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv
from paperbot.bot import fetch_papers, formatted_text, prepare_fetched_papers, read_fetched_papers

logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def paperbot(ctx, query: str, limit_per_database: int = 20):
    """Fetch papers and send them to the channel."""
    output_path = "outputs/discord_bot_papers.json"
    fetch_papers(output_path, query, limit_per_database)

    papers_fetched = read_fetched_papers(output_path)
    papers = prepare_fetched_papers(papers_fetched)
    text = formatted_text(papers)

    await ctx.send(text)


"""
    References:
    - https://discordpy.readthedocs.io/en/latest/discord.html
    - https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
"""

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot.run(BOT_TOKEN)
