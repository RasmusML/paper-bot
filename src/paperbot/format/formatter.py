import datetime
import logging
from typing import Any, Literal

import paperbot.format.slack as slk
import paperbot.format.text as txt

logger = logging.getLogger(__name__)

FORMATTERS = {
    "plain": txt.format_query_paper_for_plain,
    "slack": txt.format_query_papers_for_slack,
    "discord": txt.format_query_papers_for_discord,
    "slack-fancy": slk.format_query_papers,
}


def format_query_papers(
    papers: list[dict[str, Any]],
    since: datetime.date,
    format_type: Literal["plain", "slack", "discord", "slack-fancy"] = "plain",
) -> str | list[Any]:
    """Format the fetched papers."""
    try:
        fmt = FORMATTERS[format_type]
    except KeyError as err:
        raise ValueError(f"Invalid format type: {format_type}") from err

    return fmt(papers, since)  # type: ignore
