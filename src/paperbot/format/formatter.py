import datetime
import logging
from typing import Any, Literal

from paperbot.format.slack import SlackRichTextFormatter
from paperbot.format.text import DiscordElementFormatter, PlainElementFormatter, SlackElementFormatter, TextFormatter

logger = logging.getLogger(__name__)

FORMATTERS = {
    "plain": TextFormatter(PlainElementFormatter()),
    "slack": TextFormatter(SlackElementFormatter()),
    "discord": TextFormatter(DiscordElementFormatter()),
    "slack-rich": SlackRichTextFormatter(),
}


def format_query_papers(
    papers: list[dict[str, Any]],
    since: datetime.date,
    format_type: Literal["plain", "slack", "discord", "slack-rich"] = "plain",
) -> str | list[Any]:
    """Format the fetched papers."""
    fmt = _get_formatter(format_type)
    return fmt.format_query_papers(papers, since)


def format_similar_papers(
    reference_paper: dict[str, Any] | None,
    similar_papers: list[dict[str, Any]],
    reference_paper_title: str,
    format_type: Literal["plain", "slack", "discord", "slack-rich"] = "plain",
) -> str | list[Any]:
    """Format similar papers."""
    fmt = _get_formatter(format_type)
    return fmt.format_similar_papers(reference_paper, similar_papers, reference_paper_title)


def _get_formatter(format_type: Literal["plain", "slack", "discord", "slack-rich"]) -> Any:
    try:
        return FORMATTERS[format_type]
    except KeyError as err:
        raise ValueError(f"Invalid format type: {format_type}") from err
