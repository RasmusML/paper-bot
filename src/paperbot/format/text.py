"""Text-based formatter."""

import datetime


class ElementFormatter:
    def link(self, text: str, url: str) -> str:
        """Linkify a text with a URL."""
        raise NotImplementedError

    def item(self, text: str) -> str:
        """Itemize a text."""
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """Make text bold."""
        raise NotImplementedError


class SlackElementFormatter(ElementFormatter):
    def link(self, text: str, url: str) -> str:
        return f"<{url}|{text}>" if url is not None else text

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class DiscordElementFormatter(ElementFormatter):
    def link(self, text: str, url: str) -> str:
        return f"[{text}]({url})" if url is not None else text

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"**{text}**"


class PlainElementFormatter(ElementFormatter):
    def link(self, text: str, url: str) -> str:
        return f"{text} ({url})" if url is not None else text

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class TextFormatter:
    def __init__(self, element_formatter: ElementFormatter):
        self.element_formatter = element_formatter

    def format_query_papers(self, all_papers: list[dict], since: datetime.date) -> str:
        """Format query papers."""
        return format_query_papers(all_papers, since, self.element_formatter)

    def format_similar_papers(
        self, reference_paper: dict, similar_papers: list[dict], reference_paper_title: str
    ) -> str:
        """Format similar papers."""
        return format_similar_papers(reference_paper, similar_papers, reference_paper_title, self.element_formatter)


def format_similar_papers(
    reference_paper: dict | None,
    similar_papers: list[dict],
    reference_paper_title: str,
    fmt: ElementFormatter,
) -> str:
    if reference_paper is None:
        paperbot = fmt.link("PaperBot", "https://github.com/RasmusML/paper-bot")
        reference_paper_bold = fmt.bold(reference_paper_title)
        output = f"🔍 {paperbot} failed to find {reference_paper_bold}."
        return output

    preprints = [paper for paper in similar_papers if not paper["is_paper"]]
    papers = [paper for paper in similar_papers if paper["is_paper"]]

    # header
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("PaperBot", "https://github.com/RasmusML/paper-bot")
    reference_paper_bold = fmt.bold(reference_paper_title)
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers similar to {reference_paper_bold}.\n\n"

    # rest
    output += _newline(_format_preprint_section(preprints, fmt))
    output += _format_paper_section(papers, fmt)

    return output


def format_query_papers(
    papers: list[dict],
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
    preprints: list[dict], papers: list[dict], since: datetime.date, fmt: ElementFormatter
) -> str:
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("PaperBot", "https://github.com/RasmusML/paper-bot")
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers"

    if since:
        since_date = fmt.bold(f"{since}")
        output += f" since {since_date}"

    output += ".\n"

    return output


def _format_preprint_section(preprints: list[dict], fmt: ElementFormatter) -> str:
    if not preprints:
        return ""

    preprint_items = [_format_paper_element(preprint, fmt) for preprint in preprints]
    preprint_list = "".join(preprint + "\n" for preprint in preprint_items)

    header = fmt.bold("Preprints")
    return f"📝 {header}:\n{preprint_list}\n"


def _format_paper_section(papers: list[dict], fmt: ElementFormatter) -> str:
    if not papers:
        return ""

    paper_items = [_format_paper_element(paper, fmt) for paper in papers]
    paper_list = "".join(paper + "\n" for paper in paper_items)

    header = fmt.bold("Papers")
    return f"🗞️ {header}:\n{paper_list}\n"


def _format_paper_element(paper: dict, fmt: ElementFormatter) -> str:
    title = paper["title"]
    url = paper["url"]

    link = fmt.link(title, url)
    item = fmt.item(link)
    return item
