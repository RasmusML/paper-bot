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

PAPERFIND_HELP_INFO = """
*Usage*
- Use `/paperfind <query>,<date_since>` to fetch papers.
- Example: `/paperfind ("machine learning" | "ML") + "AMP",2022-01-01`
"""

PAPERLIKE_HELP_INFO = """
*Usage*
- Use `/paperlike <reference_paper_title>` to fetch similar papers.
- Example: `/paperlike "Attention is All You Need"`
"""

TEMPLATE_QUERIES_DIR = "queries/"


load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def parse_arguments(text: str) -> list[str]:
    return text.strip().split(",")


def prepare_blocks_for_message(blocks: list[dict], max_characters_in_block_message=20_000) -> str:
    blocks_str = json.dumps(blocks)
    block_message = None if len(blocks_str) > max_characters_in_block_message else blocks_str
    return block_message


@app.command("/paperfind")
def paperfind(ack, body):
    ack()

    channel_id = body["channel_id"]
    args = parse_arguments(body["text"])

    if len(args) != 2:
        app.client.chat_postMessage(channel=channel_id, text=PAPERFIND_HELP_INFO)
        return

    query_or_filename, date_since = args

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    query = template_queries.get(query_or_filename, query_or_filename)

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        app.client.chat_postMessage(channel=channel_id, text="Invalid date format. Please use `YYYY-MM-DD`.")
        return

    try:
        papers = pb.fetch_papers_from_query(query, since=since)
    except ValueError:
        app.client.chat_postMessage(channel=channel_id, text="Invalid query. Please check the syntax.")
        return

    blocks = pb.format_query_papers(papers, since, format_type="slack-rich")
    blocks_message = prepare_blocks_for_message(blocks)

    text = pb.format_query_papers(papers, since, format_type="slack")
    app.client.chat_postMessage(channel=channel_id, text=text, blocks=blocks_message)


@app.command("/paperlike")
def paperlike(ack, body):
    ack()

    channel_id = body["channel_id"]
    args = parse_arguments(body["text"])

    if len(args) != 1:
        app.client.chat_postMessage(channel=channel_id, text=PAPERLIKE_HELP_INFO)
        return

    reference_paper_title = args[0].replace('"', "")

    reference_paper, similar_papers = pb.fetch_similar_papers(reference_paper_title, max_papers=10)
    blocks = pb.format_similar_papers(reference_paper, similar_papers, reference_paper_title, format_type="slack-rich")
    blocks_messasge = prepare_blocks_for_message(blocks)

    text = pb.format_similar_papers(reference_paper, similar_papers, reference_paper_title, format_type="slack")
    app.client.chat_postMessage(channel=channel_id, text=text, blocks=blocks_messasge)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
