import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import paperbot.clients.discord as client

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.command()
async def paperfind(ctx):
    await client.paperfind(ctx)


@bot.command()
async def paperlike(ctx):
    await client.paperlike(ctx)


@bot.command()
async def papercite(ctx):
    await client.papercite(ctx)


if __name__ == "__main__":
    bot.run(os.environ["DISCORD_BOT_TOKEN"])
