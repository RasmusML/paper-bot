import datetime
import logging
import typing
from typing import Any, Literal

from paperbot.format.text import DiscordElementFormatter, PlainElementFormatter, SlackElementFormatter, TextFormatter

logger = logging.getLogger(__name__)

FormatType = Literal["plain", "slack", "discord"]

FORMATTERS = {
    "plain": TextFormatter(PlainElementFormatter()),
    "slack": TextFormatter(SlackElementFormatter()),
    "discord": TextFormatter(DiscordElementFormatter()),
}

assert set(FORMATTERS.keys()) == set(typing.get_args(FormatType))


def format_query_papers(
    query: str | None,
    papers: list[dict[str, Any]],
    since: datetime.date,
    add_preamble: bool = True,
    format_type: FormatType = "plain",
) -> str | list[Any]:
    """Format the fetched papers."""
    fmt = _get_formatter(format_type)
    return fmt.format_query_papers(query, papers, since, add_preamble)


def format_similar_papers(
    paper: dict[str, Any] | None,
    similar_papers: list[dict[str, Any]],
    paper_title: str,
    add_preamble: bool = True,
    format_type: FormatType = "plain",
) -> str | list[Any]:
    """Format similar papers."""
    fmt = _get_formatter(format_type)
    return fmt.format_similar_papers(paper, similar_papers, paper_title, add_preamble)


def format_papers_citing(
    paper: dict[str, Any] | None,
    citing_papers: list[dict[str, Any]],
    paper_title: str,
    add_preamble: bool = True,
    format_type: FormatType = "plain",
) -> str | list[Any]:
    """Format papers citing."""
    fmt = _get_formatter(format_type)
    return fmt.format_papers_citing(paper, citing_papers, paper_title, add_preamble)


def _get_formatter(format_type: FormatType) -> Any:
    try:
        return FORMATTERS[format_type]
    except KeyError as err:
        raise ValueError(f"Invalid format type: {format_type}") from err
