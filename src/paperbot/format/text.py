"""Text-based formatter."""

import datetime


class Formatter:
    def link(self, text: str, url: str) -> str:
        """Linkify a text with a URL."""
        raise NotImplementedError

    def item(self, text: str) -> str:
        """Itemize a text."""
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """Make text bold."""
        raise NotImplementedError


class SlackFormatter(Formatter):
    def link(self, text: str, url: str) -> str:
        return f"<{url}|{text}>" if url is not None else text

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class DiscordFormatter(Formatter):
    def link(self, text: str, url: str) -> str:
        return f"[{text}]({url})" if url is not None else text

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"**{text}**"


class PlainFormatter(Formatter):
    def link(self, text: str, url: str) -> str:
        return f"{text} ({url})" if url is not None else text

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


def format_query_paper_for_plain(papers: list[dict], since: datetime.date) -> str:
    """Generate an overview of the fetched papers in plain text."""
    return _format_paper_overview(papers, since, PlainFormatter())


def format_query_papers_for_slack(papers: list[dict], since: datetime.date) -> str:
    """Generate an overview of the fetched papers in Slack format."""
    return _format_paper_overview(papers, since, SlackFormatter())


def format_query_papers_for_discord(papers: list[dict], since: datetime.date) -> str:
    """Generate an overview of the fetched papers in Discord format."""
    return _format_paper_overview(papers, since, DiscordFormatter())


def _format_paper_overview(
    papers: list[dict],
    since: datetime.date,
    fmt: Formatter,
) -> str:
    preprints = [paper for paper in papers if not paper["is_paper"]]
    papers = [paper for paper in papers if paper["is_paper"]]

    output = ""
    output += _newline(_format_summary_section(preprints, papers, since, fmt))
    output += _newline(_format_preprint_section(preprints, fmt))
    output += _format_paper_section(papers, fmt)
    return output


def _newline(text: str) -> str:
    return "" if text == "" else f"{text}\n"


def _format_summary_section(preprints: list[dict], papers: list[dict], since: datetime.date, fmt: Formatter) -> str:
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    paperbot = fmt.link("PaperBot", "https://github.com/RasmusML/paper-bot")
    output = f"🔍 {paperbot} found {n_preprints} preprints and {n_papers} papers"

    if since:
        since_date = fmt.bold(f"{since}")
        output += f" since {since_date}"

    output += ".\n"

    return output


def _format_preprint_section(preprints: list[dict], fmt: Formatter) -> str:
    if not preprints:
        return ""

    preprint_items = [_format_paper_element(preprint, fmt) for preprint in preprints]
    preprint_list = "".join(preprint + "\n" for preprint in preprint_items)

    header = fmt.bold("Preprints")
    return f"📝 {header}:\n{preprint_list}\n"


def _format_paper_section(papers: list[dict], fmt: Formatter) -> str:
    if not papers:
        return ""

    paper_items = [_format_paper_element(paper, fmt) for paper in papers]
    paper_list = "".join(paper + "\n" for paper in paper_items)

    header = fmt.bold("Papers")
    return f"🗞️ {header}:\n{paper_list}\n"


def _format_paper_element(paper: dict, fmt: Formatter) -> str:
    title = paper["title"]
    url = paper["url"]

    link = fmt.link(title, url)
    item = fmt.item(link)
    return item
