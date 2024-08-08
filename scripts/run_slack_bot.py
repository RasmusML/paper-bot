"""Script to run a Slack bot that fetches scientific papers.

References
----------
- https://slack.dev/bolt-python/concepts

"""

import datetime
import json
import logging
import os
import time

import paperbot as pb
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logger = logging.getLogger(__name__)
pb.init_bot_logger(logger, "logs/slack.log")

PAPERFIND_HELP_INFO = """
*Usage*
- Use `/paperfind <query> <date_since>` to fetch papers.
- Example: `/paperfind '("machine learning" | "ML") + "AMP"' 2022-01-01`
"""

PAPERLIKE_HELP_INFO = """
*Usage*
- Use `/paperlike <paper_title>` to fetch similar papers.
- Example: `/paperlike 'Attention is All You Need'`
"""


PAPERCITE_HELP_INFO = """
*Usage*
- Use `/papercite <paper_title>` to fetch papers citing this paper.
- Example: `/papercite 'Could a Neuroscientist Understand a Microprocessor?'`
"""


TEMPLATE_QUERIES_DIR = "queries/"

# Maximum number of papers to fetch
QUERY_PAPER_LIMIT = 100
TEMPLATE_QUERY_PAPER_LIMIT = 500
SIMILAR_PAPERS_LIMIT = 50
CITING_PAPERS_LIMIT = 50

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])


def unbold_text(text: str) -> str:
    if text.startswith("*") and text.endswith("*"):
        return text[1:-1]
    return text


def send(channel_id: str, message: str | list[str], unfurl_links=False):
    if isinstance(message, str):
        app.client.chat_postMessage(channel=channel_id, text=message, unfurl_links=unfurl_links)
        return

    # send multiple messages as a burst
    messages = list(filter(lambda x: x.strip() != "", message))

    if len(messages) == 0:
        return

    BURST_DELAY_IN_SECONDS = 1  # Slack API rate limit

    app.client.chat_postMessage(channel=channel_id, text=messages[0], unfurl_links=unfurl_links)

    for message in messages[1:]:
        time.sleep(BURST_DELAY_IN_SECONDS)
        app.client.chat_postMessage(channel=channel_id, text=message, unfurl_links=unfurl_links)


def split_into_blocks(text: str) -> list[str]:
    blocks = []

    block = []
    inside_code_block = False
    lines = text.split("\n")

    for line in lines:
        # 1. handle code block
        if line.startswith("```"):
            assert not inside_code_block

            inside_code_block = True
            block.append(line)

            continue

        if line.endswith("```"):
            assert inside_code_block

            inside_code_block = False

            block.append(line)
            blocks.append("\n".join(block))
            block = []

            continue

        if inside_code_block:
            block.append(line)
            continue

        # 2. handle normal text
        blocks += [line]

    return blocks


@app.command("/paperfind")
def paperfind(ack, body):
    ack()

    message_id = pb.create_uuid()

    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{message_id} - '/paperfind {text}'")

    try:
        args, opt_args = pb.parse_arguments(text)
    except pb.ParseException:
        send(channel_id, PAPERFIND_HELP_INFO)
        return

    if len(args) != 2:
        send(channel_id, PAPERFIND_HELP_INFO)
        return

    query_or_filename = args[0]
    date_since = args[1]
    add_preamble = "no_extra" not in opt_args
    split_message = "split" in opt_args
    show_query = "query" in opt_args

    template_queries = pb.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    query = template_queries.get(query_or_filename, query_or_filename)
    limit = TEMPLATE_QUERY_PAPER_LIMIT if query_or_filename in template_queries else QUERY_PAPER_LIMIT

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        send(channel_id, "Invalid date format. Please use `YYYY-MM-DD`.")
        return

    try:
        papers = pb.fetch_papers_from_query(query, since=since, limit=limit)
    except ValueError:
        send(channel_id, "Invalid query. Please check the syntax.")
        return
    except RuntimeError:
        send(channel_id, "Something went very wrong...")
        logger.error(f"{message_id} - Something went very wrong...")
        return

    query_to_show = query if show_query else None
    text = pb.format_query_papers(query_to_show, papers, since, add_preamble, format_type="slack")

    text_content = split_into_blocks(text) if split_message else text
    send(channel_id, text_content, unfurl_links=False)


@app.command("/paperlike")
def paperlike(ack, body):
    ack()

    message_id = pb.create_uuid()

    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{message_id} - '/paperlike {text}'")

    try:
        args, opt_args = pb.parse_arguments(text)
    except pb.ParseException:
        send(channel_id, PAPERLIKE_HELP_INFO)
        return

    if len(args) != 1:
        send(channel_id, PAPERLIKE_HELP_INFO)
        return

    # copy-pasting paper titles from a website often adds bold text.
    title = unbold_text(args[0])
    add_preamble = "no_extra" not in opt_args
    split_message = "split" in opt_args

    paper, similar_papers = pb.fetch_similar_papers(title, limit=SIMILAR_PAPERS_LIMIT)
    text = pb.format_similar_papers(paper, similar_papers, title, add_preamble, format_type="slack")

    text_content = split_into_blocks(text) if split_message else text
    send(channel_id, text_content, unfurl_links=False)


@app.command("/papercite")
def papercite(ack, body):
    ack()

    message_id = pb.create_uuid()

    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{message_id} - '/papercite {text}'")

    try:
        args, opt_args = pb.parse_arguments(text)
    except pb.ParseException:
        send(channel_id, PAPERCITE_HELP_INFO)
        return

    if len(args) != 1:
        send(channel_id, PAPERCITE_HELP_INFO)
        return

    title = unbold_text(args[0])
    add_preamble = "no_extra" not in opt_args
    split_message = "split" in opt_args

    paper, similar_papers = pb.fetch_papers_citing(title, limit=CITING_PAPERS_LIMIT)
    text = pb.format_papers_citing(paper, similar_papers, title, add_preamble, format_type="slack")

    text_content = split_into_blocks(text) if split_message else text
    send(channel_id, text_content, unfurl_links=False)


if __name__ == "__main__":
    SocketModeHandler(app, os.environ["SLACK_APP_TOKEN"]).start()
