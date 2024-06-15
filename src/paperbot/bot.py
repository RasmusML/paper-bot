import datetime
import json
import logging
import os
from typing import Literal

import findpapers

logger = logging.getLogger(__name__)


def fetch_papers(
    output_path: str,
    query: str,
    limit_per_database: int = 20,
    since: datetime.date = None,
    until: datetime.date = None,
    overwrite: bool = True,
):
    """Fetch papers and save them to a JSON file."""
    if overwrite:
        try:
            os.remove(output_path)
        except FileNotFoundError:
            pass

    findpapers.search(
        outputpath=output_path,
        query=query,
        limit_per_database=limit_per_database,
        since=since,
        until=until,
        verbose=False,
    )


def load_papers(path: str) -> dict:
    """Read and prepare the fetched papers."""
    papers_fetched = _load_cached_papers(path)
    papers = _prepare_papers(papers_fetched)
    return papers


def _load_cached_papers(path: str) -> dict:
    """Read the fetched papers from a JSON file."""
    with open(path) as f:
        results = json.load(f)
    return results


def _prepare_papers(fetched_papers: dict) -> dict:
    """Prepare the fetched papers for further processing."""
    raw_papers = fetched_papers["papers"]

    titles = _extract_field(raw_papers, "title")
    authors = _extract_field(raw_papers, "authors")
    abstracts = _extract_field(raw_papers, "abstract")
    urls = _extract_field(raw_papers, "urls")
    publication_dates = _extract_field(raw_papers, "publication_date")
    publications = _extract_field(raw_papers, "publication")
    publication_types = _extract_field(publications, "category")

    papers = [
        {
            "title": title,
            "authors": author,
            "abstract": abstract,
            "urls": url,
            "publication_type": publication_type,
            "publication_date": publication_date,
            "is_paper": publication_type == "Journal",
        }
        for title, author, abstract, url, publication_date, publication_type in zip(
            titles, authors, abstracts, urls, publication_dates, publication_types, strict=True
        )
    ]

    is_potentially_predatory = _extract_field(publications, "is_potentially_predatory")
    papers = [
        paper
        for paper, is_predatory in zip(papers, is_potentially_predatory, strict=True)
        if (is_predatory is None) or (not is_predatory)
    ]
    papers = sorted(papers, key=lambda paper: datetime.datetime.strptime(paper["publication_date"], "%Y-%m-%d"))

    metadata = {
        "since": fetched_papers.get("since"),
        "until": fetched_papers.get("until"),
    }

    return {"metadata": metadata, "papers": papers}


def _extract_field(list_of_dics: list[dict], field: str) -> list:
    return [_dict.get(field) if _dict is not None else None for _dict in list_of_dics]


def format_paper_overview(raw_papers: dict, format_type: Literal["plain", "slack", "discord"] = "plain") -> str:
    """Generate an overview of the fetched papers."""
    assert "metadata" in raw_papers, "The input dictionary must contain a 'metadata' key."
    assert "papers" in raw_papers, "The input dictionary must contain a 'papers' key."

    FORMAT_TYPES = {
        "plain": PlainFormatter(),
        "slack": SlackFormatter(),
        "discord": DiscordFormatter(),
    }

    if format_type not in FORMAT_TYPES:
        raise ValueError(f"Formatter {format_type} is not supported.")

    formatter = FORMAT_TYPES[format_type]

    metadata = raw_papers["metadata"]
    papers_fetched = raw_papers["papers"]

    preprints = [paper for paper in papers_fetched if not paper["is_paper"]]
    papers = [paper for paper in papers_fetched if paper["is_paper"]]

    since = metadata.get("since")

    output = ""
    output += _divide(_format_summary_section(preprints, papers, since, formatter))
    output += _divide(_format_preprint_section(preprints, formatter))
    output += _format_paper_section(papers, formatter)
    return output


def _divide(text: str) -> str:
    return "" if text == "" else f"{text}\n"


def _format_summary_section(
    preprints: list[dict], papers: list[dict], since: datetime.date, formatter: "Formatter"
) -> str:
    output = f"🔍 Found {len(preprints)} preprints and {len(papers)} papers"

    if since:
        output += f" since {since}"

    output += ".\n"

    return output


def _format_preprint_section(preprints: list[dict], formatter: "Formatter") -> str:
    if not preprints:
        return ""

    preprint_items = [_format_paper_element(preprint, formatter) for preprint in preprints]
    preprint_list = "".join(preprint + "\n" for preprint in preprint_items)

    header = formatter.bold("Preprints")
    return f"📄 {header}:\n{preprint_list}\n"


def _format_paper_section(papers: list[dict], formatter: "Formatter") -> str:
    if not papers:
        return ""

    paper_items = [_format_paper_element(paper, formatter) for paper in papers]
    paper_list = "".join(paper + "\n" for paper in paper_items)

    header = formatter.bold("Papers")
    return f"📝 {header}:\n{paper_list}\n"


def _format_paper_element(paper: dict, formatter: "Formatter") -> str:
    title = paper["title"]
    urls = paper["urls"]
    url = urls[-1] if len(urls) > 0 else None

    link = formatter.linkify(title, url)
    item = formatter.itemize(link)
    return item


class Formatter:
    def linkify(self, text: str, url: str) -> str:
        """Linkify a text with a URL."""
        raise NotImplementedError

    def itemize(self, text: str) -> str:
        """Itemize a text."""
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """Bold a text."""
        raise NotImplementedError


class SlackFormatter(Formatter):
    def linkify(self, text: str, url: str) -> str:
        return f"<{url}|{text}>" if url is not None else text

    def itemize(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"


class DiscordFormatter(Formatter):
    def linkify(self, text: str, url: str) -> str:
        return f"[{text}]({url})" if url is not None else text

    def itemize(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"**{text}**"


class PlainFormatter(Formatter):
    def linkify(self, text: str, url: str) -> str:
        return f"{text} ({url})" if url is not None else text

    def itemize(self, text: str) -> str:
        return f"- {text}"

    def bold(self, text: str) -> str:
        return f"*{text}*"
