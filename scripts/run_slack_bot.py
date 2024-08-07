"""Script to run a Slack bot that fetches scientific papers.

References
----------
- https://slack.dev/bolt-python/concepts

"""

import datetime
import json
import logging
import os

import paperbot as pb
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger(__name__)
pb.init_bot_logger(logger, "logs/slack.log")

PAPERFIND_HELP_INFO = """
*Usage*
- Use `/paperfind <query>,<date_since>` to fetch papers.
- Example: `/paperfind ("machine learning" | "ML") + "AMP",2022-01-01`
"""

PAPERLIKE_HELP_INFO = """
*Usage*
- Use `/paperlike <paper_title>` to fetch similar papers.
- Example: `/paperlike "Attention is All You Need"`
"""


PAPERCITE_HELP_INFO = """
*Usage*
- Use `/papercite <paper_title>` to fetch papers cited.
- Example: `/papercite "Attention is All You Need"`
"""


TEMPLATE_QUERIES_DIR = "queries/"

# Maximum number of papers to fetch
QUERY_PAPER_LIMIT = 100
TEMPLATE_QUERY_PAPER_LIMIT = 500
SIMILAR_PAPERS_LIMIT = 50
CITING_PAPERS_LIMIT = 50

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def parse_arguments(text: str) -> list[str]:
    args = text.split(",")
    args = [arg.strip() for arg in args]
    return args


def parse_bold_text(text: str) -> str:
    if text.startswith("*") and text.endswith("*"):
        return text[1:-1]
    return text


def parse_title(title: str) -> str:
    title = title.replace('"', "")
    title = parse_bold_text(title)  # copy-pasting paper titles from a website often adds bold text.
    return title


def prepare_blocks_for_message(blocks: list[dict], max_characters_in_block_message=20_000) -> str | None:
    blocks_str = json.dumps(blocks)
    block_message = None if len(blocks_str) > max_characters_in_block_message else blocks_str
    return block_message


@app.command("/paperfind")
def paperfind(ack, body):
    ack()

    message_id = pb.create_uuid()

    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{message_id} - '/paperfind {text}'")

    args = parse_arguments(text)

    if len(args) != 2:
        app.client.chat_postMessage(channel=channel_id, text=PAPERFIND_HELP_INFO)
        return

    query_or_filename = args[0]
    date_since = args[1]

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    query = template_queries.get(query_or_filename, query_or_filename)
    limit = TEMPLATE_QUERY_PAPER_LIMIT if query_or_filename in template_queries else QUERY_PAPER_LIMIT

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        app.client.chat_postMessage(channel=channel_id, text="Invalid date format. Please use `YYYY-MM-DD`.")
        return

    try:
        papers = pb.fetch_papers_from_query(query, since=since, limit=limit)
    except ValueError:
        app.client.chat_postMessage(channel=channel_id, text="Invalid query. Please check the syntax.")
        return
    except RuntimeError:
        app.client.chat_postMessage(channel=channel_id, text="Something went very wrong...")
        logger.error(f"{message_id} - Something went very wrong...")
        return

    blocks = pb.format_query_papers(papers, since, format_type="slack-rich")
    blocks_message = prepare_blocks_for_message(blocks)

    text = pb.format_query_papers(papers, since, format_type="slack")
    app.client.chat_postMessage(channel=channel_id, text=text, blocks=blocks_message, unfurl_links=False)


@app.command("/paperlike")
def paperlike(ack, body):
    ack()

    message_id = pb.create_uuid()

    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{message_id} - '/paperlike {text}'")

    args = parse_arguments(text)

    if len(args) != 1:
        app.client.chat_postMessage(channel=channel_id, text=PAPERLIKE_HELP_INFO)
        return

    title = parse_title(args[0])

    paper, similar_papers = pb.fetch_similar_papers(title, limit=SIMILAR_PAPERS_LIMIT)
    blocks = pb.format_similar_papers(paper, similar_papers, title, format_type="slack-rich")
    blocks_message = prepare_blocks_for_message(blocks)

    text = pb.format_similar_papers(paper, similar_papers, title, format_type="slack")
    app.client.chat_postMessage(channel=channel_id, text=text, blocks=blocks_message, unfurl_links=False)


@app.command("/papercite")
def papercite(ack, body):
    ack()

    message_id = pb.create_uuid()

    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{message_id} - '/papercite {text}'")

    args = parse_arguments(text)

    if len(args) != 1:
        app.client.chat_postMessage(channel=channel_id, text=PAPERCITE_HELP_INFO)
        return

    title = parse_title(args[0])

    paper, similar_papers = pb.fetch_papers_citing(title, limit=CITING_PAPERS_LIMIT)
    blocks = pb.format_papers_citing(paper, similar_papers, title, format_type="slack-rich")
    blocks_message = prepare_blocks_for_message(blocks)

    text = pb.format_papers_citing(paper, similar_papers, title, format_type="slack")
    app.client.chat_postMessage(channel=channel_id, text=text, blocks=blocks_message, unfurl_links=False)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
