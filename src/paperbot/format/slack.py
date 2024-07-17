"""Slack Rich-text based formatter."""

import datetime
from typing import Any

import paperbot.format.rich_text as rt


class SlackRichTextFormatter:
    def format_query_papers(self, all_papers: list[dict], since: datetime.date) -> list[Any]:
        """Format query papers."""
        return format_query_papers(all_papers, since)

    def format_similar_papers(
        self, reference_paper: dict, similar_papers: list[dict], reference_paper_title: str
    ) -> list[Any]:
        """Format similar papers."""
        return format_similar_papers(reference_paper, similar_papers, reference_paper_title)


def format_similar_papers(
    reference_paper: dict | None, similar_papers: list[dict], reference_paper_title: str
) -> list[Any]:
    if reference_paper is None:
        header = [
            rt.text("\n\n🔍 "),
            rt.link("https://github.com/RasmusML/paper-bot", "PaperBot"),
            rt.text(" failed to find "),
            rt.text(f"{reference_paper_title}", rt.style(bold=True)),
            rt.text("."),
        ]

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
        rt.text(f"{reference_paper_title}", rt.style(bold=True)),
        rt.text(".\n\n"),
    ]

    # preprints section
    preprints_list = _format_preprints_section(preprints)

    # papers section
    papers_list = _format_papers_section(papers)

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


def format_query_papers(all_papers: list[dict], since: datetime.date) -> list[Any]:
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
    preprints_list = _format_preprints_section(preprints)

    # papers section
    papers_list = _format_papers_section(papers)

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


def _format_preprints_section(preprints: list[dict]) -> list[Any]:
    preprint_list = [
        rt.text("\n\n\n"),
        rt.text("Preprints", rt.style(bold=True)),
        rt.text("\n\n"),
    ]
    for preprint in preprints:
        preprint_list += _format_preprint_element(preprint)

    return preprint_list


def _format_papers_section(papers: list[dict]) -> list[Any]:
    papers_list = [
        rt.text("\n\n\n"),
        rt.text("Papers", rt.style(bold=True)),
        rt.text("\n\n"),
    ]
    for paper in papers:
        papers_list += _format_paper_element(paper)

    return papers_list


def _format_preprint_element(paper: dict) -> list[Any]:
    return [
        rt.text("📝 "),
        rt.link(paper["url"], paper["title"]),
        rt.text("\n\n"),
    ]


def _format_paper_element(paper: dict) -> list[Any]:
    return [
        rt.text("🗞️ "),
        rt.link(paper["url"], paper["title"]),
        rt.text("\n\n"),
    ]
