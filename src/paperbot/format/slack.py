"""Slack Rich-text based formatter."""

import datetime
from typing import Any

import paperbot.format.rich_text as rt


class SlackRichTextFormatter:
    def format_query_papers(
        self,
        all_papers: list[dict[str, Any]],
        since: datetime.date,
        add_preamble: bool = True,
    ) -> list[Any]:
        """Format query papers."""
        return format_query_papers(all_papers, since, add_preamble)

    def format_similar_papers(
        self,
        paper: dict[str, Any] | None,
        similar_papers: list[dict[str, Any]],
        paper_title: str,
        add_preamble: bool = True,
    ) -> list[Any]:
        """Format similar papers."""
        return format_similar_papers(paper, similar_papers, paper_title, add_preamble)

    def format_papers_citing(
        self,
        paper: dict[str, Any] | None,
        citing_papers: list[dict[str, Any]],
        paper_title: str,
        add_preamble: bool = True,
    ) -> list[Any]:
        """Format papers citing."""
        return format_papers_citing(paper, citing_papers, paper_title, add_preamble)


def format_similar_papers(
    paper: dict[str, Any] | None,
    similar_papers: list[dict[str, Any]],
    paper_title: str,
    add_preamble: bool,
) -> list[Any]:
    if paper is None:
        header = _format_failed_to_find_paper_title(paper_title)
        blocks = [rt.rich_text_block([rt.rich_text_section(header)])]
        return blocks

    preprints = [paper for paper in similar_papers if not paper["is_paper"]]
    papers = [paper for paper in similar_papers if paper["is_paper"]]

    n_preprints = len(preprints)
    n_papers = len(papers)

    # header section
    header = [
        rt.text("\n\n🔍 "),
        rt.link("https://github.com/RasmusML/paper-bot", "PaperBot"),
        rt.text(" found "),
        rt.text(f"{n_preprints}", rt.style(bold=True)),
        rt.text(" preprints and "),
        rt.text(f"{n_papers}", rt.style(bold=True)),
        rt.text(" papers similar to "),
        rt.text(f"{paper_title}", rt.style(bold=True)),
        rt.text(".\n\n"),
    ]

    # preprints section
    preprints_list = _format_preprints_section(preprints, add_preamble)

    # papers section
    papers_list = _format_papers_section(papers, add_preamble)

    # combine sections
    blocks = []
    blocks += [rt.rich_text_block([rt.rich_text_section(header)])]

    if n_preprints > 0:
        blocks += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(preprints_list)]),
        ]

    if n_papers > 0:
        blocks += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(papers_list)]),
        ]

    blocks += [rt.divider_block()]

    return blocks


def format_papers_citing(
    paper: dict[str, Any] | None,
    citing_papers: list[dict[str, Any]],
    paper_title: str,
    add_preamble: bool,
) -> list[Any]:
    if paper is None:
        header = _format_failed_to_find_paper_title(paper_title)
        blocks = [rt.rich_text_block([rt.rich_text_section(header)])]
        return blocks

    preprints = [paper for paper in citing_papers if not paper["is_paper"]]
    papers = [paper for paper in citing_papers if paper["is_paper"]]

    n_preprints = len(preprints)
    n_papers = len(papers)

    # header section
    header = [
        rt.text("\n\n🔍 "),
        rt.link("https://github.com/RasmusML/paper-bot", "PaperBot"),
        rt.text(" found "),
        rt.text(f"{n_preprints}", rt.style(bold=True)),
        rt.text(" preprints and "),
        rt.text(f"{n_papers}", rt.style(bold=True)),
        rt.text(" papers citing "),
        rt.text(f"{paper_title}", rt.style(bold=True)),
        rt.text(".\n\n"),
    ]

    # preprints section
    preprints_list = _format_preprints_section(preprints, add_preamble)

    # papers section
    papers_list = _format_papers_section(papers, add_preamble)

    # combine sections
    blocks = []
    blocks += [rt.rich_text_block([rt.rich_text_section(header)])]

    if n_preprints > 0:
        blocks += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(preprints_list)]),
        ]

    if n_papers > 0:
        blocks += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(papers_list)]),
        ]

    blocks += [rt.divider_block()]

    return blocks


def format_query_papers(all_papers: list[dict[str, Any]], since: datetime.date, add_preamble: bool) -> list[Any]:
    preprints = [paper for paper in all_papers if not paper["is_paper"]]
    papers = [paper for paper in all_papers if paper["is_paper"]]

    n_preprints = len(preprints)
    n_papers = len(papers)

    # header section
    header = [
        rt.text("\n\n🔍 "),
        rt.link("https://github.com/RasmusML/paper-bot", "PaperBot"),
        rt.text(" found "),
        rt.text(f"{n_preprints}", rt.style(bold=True)),
        rt.text(" preprints and "),
        rt.text(f"{n_papers}", rt.style(bold=True)),
        rt.text(" papers"),
    ]

    if since:
        header += [rt.text(" since "), rt.text(f"{since}", rt.style(bold=True))]

    header += [rt.text(".\n\n")]

    # preprints section
    preprints_list = _format_preprints_section(preprints, add_preamble)

    # papers section
    papers_list = _format_papers_section(papers, add_preamble)

    # combine sections
    blocks = []
    blocks += [rt.rich_text_block([rt.rich_text_section(header)])]

    if n_preprints > 0:
        blocks += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(preprints_list)]),
        ]

    if n_papers > 0:
        blocks += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(papers_list)]),
        ]

    blocks += [rt.divider_block()]

    return blocks


def _format_preprints_section(preprints: list[dict[str, Any]], add_preamble: bool) -> list[Any]:
    preprint_list = [
        rt.text("\n\n\n"),
        rt.text("Preprints", rt.style(bold=True)),
        rt.text("\n\n"),
    ]

    for preprint in preprints:
        preprint_list += _format_preprint_element(preprint, add_preamble)

    return preprint_list


def _format_papers_section(papers: list[dict[str, Any]], add_preamble: bool) -> list[Any]:
    papers_list = [
        rt.text("\n\n\n"),
        rt.text("Papers", rt.style(bold=True)),
        rt.text("\n\n"),
    ]
    for paper in papers:
        papers_list += _format_paper_element(paper, add_preamble)

    return papers_list


def _format_preprint_element(paper: dict[str, Any], add_preamble: bool) -> list[Any]:
    elements = []

    url = paper["url"]
    title = paper["title"]

    if add_preamble:
        citations = paper["citation_count"]
        publication_date = paper.get("publication_date")

        date = _format_paper_publication_date(publication_date)
        elements += [rt.text("📅 "), rt.text(f"{date}, "), rt.text("💬 "), rt.text(f"{citations}\n")]

    elements += [
        rt.text("📝 "),
        rt.link(url, title),
    ]
    elements += [rt.text("\n\n\n\n")] if add_preamble else [rt.text("\n\n")]

    return elements


def _format_paper_publication_date(date: str | None) -> str:
    if date is None:
        return "????"

    date_format = datetime.datetime.strptime(date, "%Y-%m-%d")
    return date_format.strftime("%Y")


def _format_paper_element(paper: dict[str, Any], add_preamble: bool) -> list[Any]:
    elements = []

    url = paper["url"]
    title = paper["title"]

    if add_preamble:
        citations = paper["citation_count"]
        publication_date = paper.get("publication_date")

        date = _format_paper_publication_date(publication_date)
        elements += [rt.text("📅 "), rt.text(f"{date}, "), rt.text("💬 "), rt.text(f"{citations}\n")]

    elements += [
        rt.text("🗞️ "),
        rt.link(url, title),
    ]
    elements += [rt.text("\n\n\n\n")] if add_preamble else [rt.text("\n\n")]

    return elements


def _format_failed_to_find_paper_title(paper_title: str) -> list[Any]:
    return [
        rt.text("\n\n🔍 "),
        rt.link("https://github.com/RasmusML/paper-bot", "PaperBot"),
        rt.text(" failed to find "),
        rt.text(f"{paper_title}", rt.style(bold=True)),
        rt.text("."),
    ]
