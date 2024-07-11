"""Slack Rich-text based formatter."""

import datetime
from typing import Any

import paperbot.formatter.rich_text as rt


def format_paper_overview(all_papers: list[dict], since: datetime.date) -> list[Any]:
    preprints = [paper for paper in all_papers if not paper["is_paper"]]
    papers = [paper for paper in all_papers if paper["is_paper"]]

    # header section
    n_preprints = len(preprints)
    n_papers = len(papers)

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
    preprint_list = [
        rt.text("\n\n\n"),
        rt.text("Preprints", rt.style(bold=True)),
        rt.text("\n\n"),
    ]
    for preprint in preprints:
        preprint_list += _format_preprint_element(preprint)

    # papers section
    papers_list = [
        rt.text("\n\n\n"),
        rt.text("Papers", rt.style(bold=True)),
        rt.text("\n\n"),
    ]
    for paper in papers:
        papers_list += _format_paper_element(paper)

    # combine sections
    result = []
    result += [rt.rich_text_block([rt.rich_text_section(header)])]

    if n_preprints > 0:
        result += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(preprint_list)]),
        ]

    if n_papers > 0:
        result += [
            rt.divider_block(),
            rt.rich_text_block([rt.rich_text_section(papers_list)]),
        ]

    result += [rt.divider_block()]

    return result


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
