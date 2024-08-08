"""Text-based formatter."""

import datetime
from typing import Any


class ElementFormatter:
    def link(self, url: str, text: str = None) -> str:
        """Linkify an url with optional alias text."""
        raise NotImplementedError

    def item(self, text: str) -> str:
        """Itemize a text."""
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """Make text bold."""
        raise NotImplementedError


class SlackElementFormatter(ElementFormatter):
    def link(self, url: str, text: str = None) -> str:
        return f"<{url}|{text}>" if text is not None else url

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class DiscordElementFormatter(ElementFormatter):
    def link(self, url: str, text: str = None) -> str:
        return f"[{text}](<{url}>)" if text is not None else f"<{url}>"

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"**{text}**"


class PlainElementFormatter(ElementFormatter):
    def link(self, url: str, text: str = None) -> str:
        return f"{text} ({url})" if text is not None else url

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class TextFormatter:
    def __init__(self, element_formatter: ElementFormatter):
        self.element_formatter = element_formatter

    def format_query_papers(
        self,
        all_papers: list[dict[str, Any]],
        since: datetime.date,
        add_preamble: bool = True,
    ) -> str:
        """Format query papers."""
        return format_query_papers(all_papers, since, add_preamble, self.element_formatter)

    def format_similar_papers(
        self,
        paper: dict[str, Any] | None,
        similar_papers: list[dict[str, Any]],
        paper_title: str,
        add_preamble: bool = True,
    ) -> str:
        """Format similar papers."""
        return format_similar_papers(paper, similar_papers, paper_title, add_preamble, self.element_formatter)

    def format_papers_citing(
        self,
        paper: dict[str, Any] | None,
        citing_papers: list[dict[str, Any]],
        paper_title: str,
        add_preamble: bool = True,
    ) -> str:
        """Format papers citing."""
        return format_papers_citing(paper, citing_papers, paper_title, add_preamble, self.element_formatter)


def format_papers_citing(
    paper: dict[str, Any] | None,
    citing_papers: list[dict[str, Any]],
    paper_title: str,
    add_preamble: bool,
    fmt: ElementFormatter,
) -> str:
    if paper is None:
        return _format_failed_to_find_paper_title(paper_title, fmt)

    preprints = [paper for paper in citing_papers if not paper["is_paper"]]
    papers = [paper for paper in citing_papers if paper["is_paper"]]

    # header
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    paper_bold = fmt.bold(paper_title)
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers citing {paper_bold}.\n\n"

    # rest
    output += _divider(_format_preprint_section(preprints, add_preamble, fmt))
    output += _format_paper_section(papers, add_preamble, fmt)

    return output


def format_similar_papers(
    paper: dict[str, Any] | None,
    similar_papers: list[dict[str, Any]],
    paper_title: str,
    add_preamble: bool,
    fmt: ElementFormatter,
) -> str:
    if paper is None:
        return _format_failed_to_find_paper_title(paper_title, fmt)

    preprints = [paper for paper in similar_papers if not paper["is_paper"]]
    papers = [paper for paper in similar_papers if paper["is_paper"]]

    # header
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    paper_bold = fmt.bold(paper_title)
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers similar to {paper_bold}.\n\n"

    # rest
    output += _divider(_format_preprint_section(preprints, add_preamble, fmt))
    output += _format_paper_section(papers, add_preamble, fmt)

    return output


def _format_failed_to_find_paper_title(paper_title: str, fmt: ElementFormatter) -> str:
    paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    paper_bold = fmt.bold(paper_title)
    output = f"🔍 {paperbot} failed to find {paper_bold}."
    return output


def format_query_papers(
    papers: list[dict[str, Any]],
    since: datetime.date,
    add_preamble: bool,
    fmt: ElementFormatter,
) -> str:
    preprints = [paper for paper in papers if not paper["is_paper"]]
    papers = [paper for paper in papers if paper["is_paper"]]

    output = ""
    output += _divider(_format_query_header_section(preprints, papers, since, fmt))
    output += _divider(_format_preprint_section(preprints, add_preamble, fmt))
    output += _format_paper_section(papers, add_preamble, fmt)
    return output


def _divider(text: str) -> str:
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


def _format_preprint_section(preprints: list[dict[str, Any]], add_preamble: bool, fmt: ElementFormatter) -> str:
    if not preprints:
        return ""

    preprint_items = [_format_preprint_element(preprint, add_preamble, fmt) for preprint in preprints]
    preprint_list = "".join(preprint for preprint in preprint_items)
    preprint_list = preprint_list.rstrip("\n")

    header = fmt.bold("Preprints")
    return f"{header}\n{preprint_list}\n"


def _format_preprint_element(paper: dict[str, Any], add_preamble: bool, fmt: ElementFormatter) -> str:
    output = ""

    url = paper["url"]
    title = paper["title"]

    link = fmt.link(url, title)
    output += f"📝 {link}"

    if add_preamble:
        citations = paper.get("citation_count", "?")
        publication_date = paper.get("publication_date", "?")
        reference_count = paper.get("reference_count", "?")

        date = _format_paper_publication_date(publication_date)
        output += f"｜📅 {date}｜📚{reference_count}｜💬 {citations}｜"
        output += "\n"

    output += "\n"

    return output


def _format_paper_section(papers: list[dict[str, Any]], add_preamable: bool, fmt: ElementFormatter) -> str:
    if not papers:
        return ""

    paper_items = [_format_paper_element(paper, add_preamable, fmt) for paper in papers]
    paper_list = "".join(paper for paper in paper_items)
    paper_list = paper_list.rstrip("\n")

    header = fmt.bold("Papers")
    return f"{header}\n{paper_list}\n"


def _format_paper_element(paper: dict[str, Any], add_preamble: bool, fmt: ElementFormatter) -> str:
    output = ""

    url = paper["url"]
    title = paper["title"]

    link = fmt.link(url, title)
    output += f"🗞️ {link}"

    if add_preamble:
        citations = paper.get("citation_count", "?")
        publication_date = paper.get("publication_date", "?")
        reference_count = paper.get("reference_count", "?")

        date = _format_paper_publication_date(publication_date)
        output += f"｜📅 {date}｜📚{reference_count}｜💬 {citations}｜"
        output += "\n"

    output += "\n"

    return output


def _format_paper_publication_date(date: str | None) -> str:
    if date is None:
        return "????-??"

    date_format = datetime.datetime.strptime(date, "%Y-%m-%d")
    return date_format.strftime("%Y-%m")
