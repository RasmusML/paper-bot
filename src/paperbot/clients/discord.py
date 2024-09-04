import asyncio
import datetime
import logging
import os

import requests

import paperbot as pb
from paperbot import ArgumentParserException

logger = logging.getLogger(__name__)

PAPERFIND_HELP_INFO = """
**Usage**
- Use `!paperfind <query> <since>` to fetch papers.
- Example: `!paperfind '("machine learning" | "ML") + "AMP"' 2022-01-01`
"""

PAPERLIKE_HELP_INFO = """
**Usage**
- Use `!paperlike <title>` to fetch similar papers.
- Example: `!paperlike 'Attention is All You Need'`
"""

PAPERCITE_HELP_INFO = """
**Usage**
- Use `!papercite <title>` to fetch papers citing this paper.
- Example: `!papercite 'Could a Neuroscientist Understand a Microprocessor?'`
"""

DELAY_BETWEEN_MESSAGES_IN_SECONDS = 0.1  # Discord API rate limit
MAX_MESSAGE_LENGTH = 2_000  # Discord max message length


async def paperfind(
    ctx,
    *,
    query_paper_limit: int = 100,
    template_query_paper_limit: int = 500,
    support_split_flag: bool = True,
    template_queries_path: str = "queries",
):
    """Fetch papers and send them to the channel."""
    user = ctx.author.name

    raw_arguments = _get_raw_arguments(ctx)
    logger.info(f"{user} - '!paperfind {raw_arguments}'")

    try:
        args, opt_args = pb.parse_arguments(raw_arguments)
    except ArgumentParserException:
        await _send(ctx, PAPERFIND_HELP_INFO)
        return

    if len(args) != 2:
        await _send(ctx, PAPERFIND_HELP_INFO)
        return

    query_or_template = args[0]
    date_since = args[1]
    add_preamble = "no_extra" not in opt_args
    split_message = "split" in opt_args
    is_template = "template" in opt_args
    show_query = support_split_flag and "no_query" not in opt_args

    if is_template:
        template_queries = pb.read_queries_from_dir(template_queries_path)

        if query_or_template not in template_queries:
            path = os.path.join(template_queries_path, f"{query_or_template}.txt")
            path = path.replace("\n", "\\n")
            await _send(ctx, f"Template query `{path}` not found.")
            return

        query = template_queries[query_or_template]
        limit = template_query_paper_limit
    else:
        query = query_or_template
        limit = query_paper_limit

    try:
        since = datetime.date.fromisoformat(date_since)
    except ValueError:
        await _send(ctx, "Invalid date format. Please use YYYY-MM-DD.")
        return

    try:
        papers = pb.fetch_papers_from_query(query, since=since, limit=limit)
    except requests.exceptions.RequestException:
        await _send(ctx, "Request to Semantic Scholar failed. Please try again later.")
        return

    query_to_show = query if show_query else None
    text = pb.format_query_papers(query_to_show, papers, since, add_preamble, "discord")

    text_content = _split_into_blocks(text) if split_message else text
    await _send(ctx, text_content)  # type: ignore


async def paperlike(ctx, *, paper_limit: int = 50):
    """Fetch similar papers and send them to the channel."""
    user = ctx.author.name

    raw_arguments = _get_raw_arguments(ctx)
    logger.info(f"{user} - '!paperlike {raw_arguments}'")

    try:
        args, opt_args = pb.parse_arguments(raw_arguments)
    except ArgumentParserException:
        await _send(ctx, PAPERLIKE_HELP_INFO)
        return

    if len(args) != 1:
        await _send(ctx, PAPERLIKE_HELP_INFO)
        return

    title = args[0]
    add_preamble = "no_extra" not in opt_args
    split_message = "split" in opt_args

    try:
        paper, similar_papers = pb.fetch_similar_papers(title, limit=paper_limit)
    except requests.exceptions.RequestException:
        await _send(ctx, "Request to Semantic Scholar failed. Please try again later.")
        return

    text = pb.format_similar_papers(paper, similar_papers, title, add_preamble, "discord")
    text_content = _split_into_blocks(text) if split_message else text
    await _send(ctx, text_content)  # type: ignore


async def papercite(ctx, *, paper_limit: int = 50):
    """Fetch similar papers and send them to the channel."""
    user = ctx.author.name

    raw_arguments = _get_raw_arguments(ctx)
    logger.info(f"{user} - '!papercite {raw_arguments}'")

    try:
        args, opt_args = pb.parse_arguments(raw_arguments)
    except ArgumentParserException:
        await _send(ctx, PAPERCITE_HELP_INFO)
        return

    if len(args) != 1:
        await _send(ctx, PAPERCITE_HELP_INFO)
        return

    title = args[0]
    add_preamble = "no_extra" not in opt_args
    split_message = "split" in opt_args

    try:
        paper, similar_papers = pb.fetch_papers_citing(title, limit=paper_limit)
    except requests.exceptions.RequestException:
        await _send(ctx, "Request to Semantic Scholar failed. Please try again later.")
        return

    text = pb.format_papers_citing(paper, similar_papers, title, add_preamble, "discord")
    text_content = _split_into_blocks(text) if split_message else text
    await _send(ctx, text_content)  # type: ignore


async def _send(ctx, text: str | list[str]):
    messages = [text] if isinstance(text, str) else text

    for message in messages:
        sendable_messages = _break_text_with_newlines(message, max_length=MAX_MESSAGE_LENGTH)
        sendable_messages = list(filter(lambda s: s.strip() != "", sendable_messages))

        for sendable_message in sendable_messages:
            await asyncio.sleep(DELAY_BETWEEN_MESSAGES_IN_SECONDS)
            await ctx.send(sendable_message)


def _get_raw_arguments(ctx) -> str:
    args = ctx.message.content.split(" ")[1:]
    return " ".join(args)


def _break_text(text: str, max_length: int) -> list[str]:
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def _break_text_with_newlines(text: str, max_length: int) -> list[str]:
    texts = []

    lines = text.split("\n")

    text_builder = lines[0]
    for line in lines[1:]:
        if len(text_builder) > max_length:
            texts += _break_text(text_builder, max_length)
            text_builder = ""
        elif len(text_builder) + len(line) > max_length:
            texts += [text_builder]
            text_builder = ""
        text_builder += "\n" + line

    texts += _break_text(text_builder, max_length)

    return texts


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
