import logging
import os

import discord
import paperbot as pb
from discord.ext import commands
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command()
async def paperbot(ctx, query: str, limit_per_database: int = 20):
    """Fetch papers and send them to the channel."""
    output_path = "outputs/discord_bot_papers.json"
    pb.fetch_papers(output_path, query, limit_per_database)

    papers = pb.get_fetched_papers(output_path)
    text = pb.formatted_text(papers)

    await ctx.send(text)


"""
    References:
    - https://discordpy.readthedocs.io/en/latest/discord.html
    - https://discordpy.readthedocs.io/en/latest/ext/commands/commands.html
"""

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    bot.run(BOT_TOKEN)
