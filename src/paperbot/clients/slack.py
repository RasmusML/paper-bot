import datetime
import logging
import os
import time
from typing import Any

import requests
from slack_bolt.app import App

import paperbot as pb
from paperbot import ArgumentParserException

logger = logging.getLogger(__name__)

PAPERFIND_HELP_INFO = """
*Usage*
- Use `/paperfind <query> <since>` to fetch papers.
- Example: `/paperfind '("machine learning" | "ML") + "AMP"' 2022-01-01`
"""

PAPERLIKE_HELP_INFO = """
*Usage*
- Use `/paperlike <title>` to fetch similar papers.
- Example: `/paperlike 'Attention is All You Need'`
"""


PAPERCITE_HELP_INFO = """
*Usage*
- Use `/papercite <title>` to fetch papers citing this paper.
- Example: `/papercite 'Could a Neuroscientist Understand a Microprocessor?'`
"""

DELAY_BETWEEN_MESSAGES_IN_SECONDS = 1  # Slack API rate limit


def paperfind(
    app: App,
    body: dict[str, Any],
    *,
    query_paper_limit: int = 100,
    template_query_paper_limit: int = 500,
    support_split_flag: bool = True,
    template_queries_path: str = "queries/",
):
    user = body["user_name"]
    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{user} - '/paperfind {text}'")

    try:
        args, opt_args = pb.parse_arguments(text)
    except ArgumentParserException:
        _send_message(app, channel_id, PAPERFIND_HELP_INFO)
        return

    if len(args) != 2:
        _send_message(app, channel_id, PAPERFIND_HELP_INFO)
        return

    query_or_template = args[0]
    date_since = args[1]

    add_preamble = "no_extra" not in opt_args
    show_query = "no_query" not in opt_args
    is_template = "template" in opt_args
    split_message = support_split_flag and "split" in opt_args

    if is_template:
        template_queries = pb.read_queries_from_dir(template_queries_path)

        if query_or_template not in template_queries:
            path = os.path.join(template_queries_path, f"{query_or_template}.txt")
            path = path.replace("\n", "\\n")
            _send_message(app, channel_id, f"Template query `{path}` not found.")
            return

        query = template_queries[query_or_template]
        limit = template_query_paper_limit
    else:
        query = query_or_template
        limit = query_paper_limit

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        _send_message(app, channel_id, "Invalid date format. Please use `YYYY-MM-DD`.")
        return

    try:
        papers = pb.fetch_papers_from_query(query, since=since, limit=limit)
    except requests.exceptions.RequestException:
        _send_message(app, channel_id, "Request to Semantic Scholar failed. Please try again later.")
        return

    query_to_show = query if show_query else None
    text = pb.format_query_papers(query_to_show, papers, since, add_preamble, format_type="slack")

    text_content = _split_into_blocks(text) if split_message else text
    _send_message(app, channel_id, text_content, unfurl_links=False)


def paperlike(app: App, body: dict[str, Any], *, paper_limit: int = 50, support_split_flag: bool = True):
    user = body["user_name"]
    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{user} - '/paperlike {text}'")

    try:
        args, opt_args = pb.parse_arguments(text)
    except ArgumentParserException:
        _send_message(app, channel_id, PAPERLIKE_HELP_INFO)
        return

    if len(args) != 1:
        _send_message(app, channel_id, PAPERLIKE_HELP_INFO)
        return

    # copy-pasting paper titles from a website often adds bold text.
    title = _unbold_text(args[0])
    add_preamble = "no_extra" not in opt_args
    split_message = support_split_flag and "split" in opt_args

    try:
        paper, similar_papers = pb.fetch_similar_papers(title, limit=paper_limit)
    except requests.exceptions.RequestException:
        _send_message(app, channel_id, "Request to Semantic Scholar failed. Please try again later.")
        return

    text = pb.format_similar_papers(paper, similar_papers, title, add_preamble, format_type="slack")

    text_content = _split_into_blocks(text) if split_message else text
    _send_message(app, channel_id, text_content, unfurl_links=False)


def papercite(app: App, body: dict[str, Any], *, paper_limit: int = 50, support_split_flag: bool = True):
    user = body["user_name"]
    channel_id = body["channel_id"]
    text = body["text"]

    logger.info(f"{user} - '/papercite {text}'")

    try:
        args, opt_args = pb.parse_arguments(text)
    except ArgumentParserException:
        _send_message(app, channel_id, PAPERCITE_HELP_INFO)
        return

    if len(args) != 1:
        _send_message(app, channel_id, PAPERCITE_HELP_INFO)
        return

    title = _unbold_text(args[0])
    add_preamble = "no_extra" not in opt_args
    split_message = support_split_flag and "split" in opt_args

    try:
        paper, similar_papers = pb.fetch_papers_citing(title, limit=paper_limit)
    except requests.exceptions.RequestException:
        _send_message(app, channel_id, "Request to Semantic Scholar failed. Please try again later.")
        return

    text = pb.format_papers_citing(paper, similar_papers, title, add_preamble, format_type="slack")

    text_content = _split_into_blocks(text) if split_message else text
    _send_message(app, channel_id, text_content, unfurl_links=False)


def _unbold_text(text: str) -> str:
    if text.startswith("*") and text.endswith("*"):
        return text[1:-1]
    return text


def _send_message(app: App, channel_id: str, message: str | list[str], unfurl_links=False):
    if isinstance(message, str):
        app.client.chat_postMessage(channel=channel_id, text=message, unfurl_links=unfurl_links)
        return

    # send multiple messages as a burst
    messages = list(filter(lambda x: x.strip() != "", message))

    if len(messages) == 0:
        return

    app.client.chat_postMessage(channel=channel_id, text=messages[0], unfurl_links=unfurl_links)

    for message in messages[1:]:
        time.sleep(DELAY_BETWEEN_MESSAGES_IN_SECONDS)
        app.client.chat_postMessage(channel=channel_id, text=message, unfurl_links=unfurl_links)


def _split_into_blocks(text: str) -> list[str]:
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
