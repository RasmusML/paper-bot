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

    def code_block(self, text: str) -> str:
        """Format as code block."""
        raise NotImplementedError


class SlackElementFormatter(ElementFormatter):
    def link(self, url: str, text: str = None) -> str:
        return f"<{url}|{text}>" if text is not None else url

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"

    def code_block(self, text: str) -> str:
        return f"```{text}```"


class DiscordElementFormatter(ElementFormatter):
    def link(self, url: str, text: str = None) -> str:
        return f"[{text}](<{url}>)" if text is not None else f"<{url}>"

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"**{text}**"

    def code_block(self, text: str) -> str:
        return f"```\n{text}```"


class PlainElementFormatter(ElementFormatter):
    def link(self, url: str, text: str = None) -> str:
        return f"{text} ({url})" if text is not None else url

    def item(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"

    def code_block(self, text: str) -> str:
        return f"`{text}`"


class TextFormatter:
    def __init__(self, element_formatter: ElementFormatter):
        self.element_formatter = element_formatter

    def format_query_papers(
        self,
        query: str | None,
        all_papers: list[dict[str, Any]],
        since: datetime.date,
        add_preamble: bool = True,
    ) -> str:
        """Format query papers."""
        return format_query_papers(query, all_papers, since, add_preamble, self.element_formatter)

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
    t_n_preprints = fmt.bold(f"{len(preprints)}")
    t_n_papers = fmt.bold(f"{len(papers)}")

    t_paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")

    if paper["is_paper"]:
        t_paper_info = _format_as_paper(paper, add_preamble, fmt)
    else:
        t_paper_info = _format_as_preprint(paper, add_preamble, fmt)

    t_preprint = "preprint" if len(preprints) == 1 else "preprints"
    t_paper = "paper" if len(papers) == 1 else "papers"

    text = f"🔍 {t_paperbot} found {t_n_preprints} {t_preprint} and {t_n_papers} {t_paper} citing {t_paper_info}\n\n"

    # rest
    text += _divide_block(_format_preprint_section(preprints, add_preamble, fmt))
    text += _format_paper_section(papers, add_preamble, fmt)

    return text


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
    t_n_preprints = fmt.bold(f"{len(preprints)}")
    t_n_papers = fmt.bold(f"{len(papers)}")

    t_paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    if paper["is_paper"]:
        t_paper_info = _format_as_paper(paper, add_preamble, fmt)
    else:
        t_paper_info = _format_as_preprint(paper, add_preamble, fmt)

    t_preprint = "preprint" if len(preprints) == 1 else "preprints"
    t_paper = "paper" if len(papers) == 1 else "papers"

    text = f"🔍 {t_paperbot} found {t_n_preprints} {t_preprint} and {t_n_papers} {t_paper} similar to {t_paper_info}.\n\n"

    # rest
    text += _divide_block(_format_preprint_section(preprints, add_preamble, fmt))
    text += _format_paper_section(papers, add_preamble, fmt)

    return text


def _format_failed_to_find_paper_title(paper_title: str, fmt: ElementFormatter) -> str:
    paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    paper_bold = fmt.bold(paper_title)
    output = f"🔍 {paperbot} failed to find {paper_bold}."
    return output


def format_query_papers(
    query: str | None,
    papers: list[dict[str, Any]],
    since: datetime.date,
    add_preamble: bool,
    fmt: ElementFormatter,
) -> str:
    preprints = [paper for paper in papers if not paper["is_paper"]]
    papers = [paper for paper in papers if paper["is_paper"]]

    text = ""
    text += _divide_block(_format_query_header_section(query, preprints, papers, since, fmt))
    text += _divide_block(_format_preprint_section(preprints, add_preamble, fmt))
    text += _format_paper_section(papers, add_preamble, fmt)
    return text


def _divide_block(text: str) -> str:
    return "" if text == "" else f"{text}\n"


def _format_query_header_section(
    query: str | None,
    preprints: list[dict[str, Any]],
    papers: list[dict[str, Any]],
    since: datetime.date,
    fmt: ElementFormatter,
) -> str:
    n_preprints = fmt.bold(f"{len(preprints)}")
    n_papers = fmt.bold(f"{len(papers)}")

    t_preprint = "preprint" if len(preprints) == 1 else "preprints"
    t_paper = "paper" if len(papers) == 1 else "papers"

    t_paperbot = fmt.link("https://github.com/RasmusML/paper-bot", "PaperBot")
    text = f"🔍 {t_paperbot} found {n_preprints} {t_preprint} and {n_papers} {t_paper}"

    if since:
        t_since_date = fmt.bold(f"{since}")
        text += f" since {t_since_date}"

    if query:
        text += " using query:\n"
        text += fmt.code_block(query)
    else:
        text += "."

    text += "\n"

    return text


def _format_preprint_section(preprints: list[dict[str, Any]], add_preamble: bool, fmt: ElementFormatter) -> str:
    if not preprints:
        return ""

    preprint_items = [_format_as_preprint(preprint, add_preamble, fmt) for preprint in preprints]
    t_preprint_list = "".join(preprint + "\n\n" for preprint in preprint_items)
    t_preprint_list = t_preprint_list.rstrip("\n")

    t_header = fmt.bold("Preprints")

    return f"{t_header}\n{t_preprint_list}\n"


def _format_as_preprint(paper: dict[str, Any], add_preamble: bool, fmt: ElementFormatter) -> str:
    text = ""

    url = paper["url"]
    title = paper["title"]

    link = fmt.link(url, title)
    text += f"📝 {link}"

    if add_preamble:
        publication_date = paper.get("publication_date")
        date = _format_paper_publication_date(publication_date)

        references = paper.get("reference_count", "?")
        citations = paper.get("citation_count", "?")

        text += f"｜📅 {date}｜📚{references}｜💬 {citations}｜"

    return text


def _format_paper_section(papers: list[dict[str, Any]], add_preamable: bool, fmt: ElementFormatter) -> str:
    if not papers:
        return ""

    paper_items = [_format_as_paper(paper, add_preamable, fmt) for paper in papers]
    paper_list = "".join(paper + "\n\n" for paper in paper_items)
    paper_list = paper_list.rstrip("\n")

    header = fmt.bold("Papers")
    return f"{header}\n{paper_list}\n"


def _format_as_paper(paper: dict[str, Any], add_preamble: bool, fmt: ElementFormatter) -> str:
    text = ""

    url = paper["url"]
    title = paper["title"]

    link = fmt.link(url, title)
    text += f"🗞️ {link}"

    if add_preamble:
        publication_date = paper.get("publication_date")
        date = _format_paper_publication_date(publication_date)

        references = paper.get("reference_count", "?")
        citations = paper.get("citation_count", "?")

        text += f"｜📅 {date}｜📚{references}｜💬 {citations}｜"

    return text


def _format_paper_publication_date(date: str | None) -> str:
    if date is None:
        return "????-??"

    date_format = datetime.datetime.strptime(date, "%Y-%m-%d")
    return date_format.strftime("%Y-%m")
