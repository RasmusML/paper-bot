"""Text-based formatter."""

import datetime
from typing import Any


class ElementFormatter:
    def link(self, url: str, text: str) -> str:
        """Linkify a text with a URL."""
        raise NotImplementedError

    def item(self, text: str) -> str:
        """Itemize a text."""
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """Make text bold."""
        raise NotImplementedError


class SlackElementFormatter(ElementFormatter):
    def link(self, url: str, text: str) -> str:
        return f"<{url}|{text}>" if text is not None else url

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class DiscordElementFormatter(ElementFormatter):
    def link(self, url: str, text: str) -> str:
        return f"[{text}](<{url}>)" if text is not None else f"<{url}>"

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"**{text}**"


class PlainElementFormatter(ElementFormatter):
    def link(self, url: str, text: str) -> str:
        return f"{text} ({url})" if text is not None else url

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class TextFormatter:
    def __init__(self, element_formatter: ElementFormatter):
        self.element_formatter = element_formatter

    def format_query_papers(self, all_papers: list[dict[str, Any]], since: datetime.date) -> str:
        """Format query papers."""
        return format_query_papers(all_papers, since, self.element_formatter)

    def format_similar_papers(
        self, paper: dict[str, Any], similar_papers: list[dict[str, Any]], paper_title: str
    ) -> str:
        """Format similar papers."""
        return format_similar_papers(paper, similar_papers, paper_title, self.element_formatter)


def format_similar_papers(
    paper: dict[str, Any] | None,
    similar_papers: list[dict[str, Any]],
    paper_title: str,
    fmt: ElementFormatter,
) -> str:
    if paper is None:
        paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
        reference_paper_bold = fmt.bold(paper_title)
        output = f"🔍 {paperbot} failed to find {reference_paper_bold}."
        return output

    preprints = [paper for paper in similar_papers if not paper["is_paper"]]
    papers = [paper for paper in similar_papers if paper["is_paper"]]

    # header
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    reference_paper_bold = fmt.bold(paper_title)
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers similar to {reference_paper_bold}.\n\n"

    # rest
    output += _newline(_format_preprint_section(preprints, fmt))
    output += _format_paper_section(papers, fmt)

    return output


def format_query_papers(
    papers: list[dict[str, Any]],
    since: datetime.date,
    fmt: ElementFormatter,
) -> str:
    preprints = [paper for paper in papers if not paper["is_paper"]]
    papers = [paper for paper in papers if paper["is_paper"]]

    output = ""
    output += _newline(_format_query_header_section(preprints, papers, since, fmt))
    output += _newline(_format_preprint_section(preprints, fmt))
    output += _format_paper_section(papers, fmt)
    return output


def _newline(text: str) -> str:
    return "" if text == "" else f"{text}\n"


def _format_query_header_section(
    preprints: list[dict[str, Any]],
    papers: list[dict[str, Any]],
    since: datetime.date,
    fmt: ElementFormatter,
) -> str:
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers"

    if since:
        since_date = fmt.bold(f"{since}")
        output += f" since {since_date}"

    output += ".\n"

    return output


def _format_preprint_section(preprints: list[dict[str, Any]], fmt: ElementFormatter) -> str:
    if not preprints:
        return ""

    preprint_items = [_format_paper_element(preprint, fmt) for preprint in preprints]
    preprint_list = "".join(preprint + "\n" for preprint in preprint_items)

    header = fmt.bold("Preprints")
    return f"📝 {header}:\n{preprint_list}\n"


def _format_paper_section(papers: list[dict[str, Any]], fmt: ElementFormatter) -> str:
    if not papers:
        return ""

    paper_items = [_format_paper_element(paper, fmt) for paper in papers]
    paper_list = "".join(paper + "\n" for paper in paper_items)

    header = fmt.bold("Papers")
    return f"🗞️ {header}:\n{paper_list}\n"


def _format_paper_element(paper: dict[str, Any], fmt: ElementFormatter) -> str:
    url = paper["url"]
    title = paper["title"]

    link = fmt.link(url, title)
    item = fmt.item(link)
    return item
