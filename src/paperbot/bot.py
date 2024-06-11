import datetime
import json
import logging
import os

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


def get_fetched_papers(path: str) -> dict:
    """Read and prepare the fetched papers."""
    papers_fetched = _read_fetched_papers(path)
    papers = _prepare_fetched_papers(papers_fetched)
    return papers


def _read_fetched_papers(path: str) -> dict:
    """Read the fetched papers from a JSON file."""
    with open(path) as f:
        results = json.load(f)
    return results


def _prepare_fetched_papers(papers_fetched: dict) -> dict:
    """Prepare the fetched papers for further processing."""
    all_papers = papers_fetched["papers"]

    titles = _extract_field(all_papers, "title")
    authors = _extract_field(all_papers, "authors")
    abstracts = _extract_field(all_papers, "abstract")
    urls = _extract_field(all_papers, "urls")
    publication_dates = _extract_field(all_papers, "publication_date")
    publications = _extract_field(all_papers, "publication")
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

    papers = sorted(papers, key=lambda x: datetime.datetime.strptime(x["publication_date"], "%Y-%m-%d"))

    metadata = {
        "since": papers_fetched.get("since"),
        "until": papers_fetched.get("until"),
    }

    return {"metadata": metadata, "papers": papers}


def _extract_field(list_of_dics: list[dict], field: str) -> list:
    return [_dict.get(field) if _dict is not None else None for _dict in list_of_dics]


def formatted_text(raw_papers: dict) -> str:
    """Generate an overview of the fetched papers."""

    def format_paper(paper):
        url_prefix = "🔗" if len(paper["urls"]) > 0 else "❌"
        output = f"- {url_prefix} {paper['title']}"
        # output += f" ({paper['urls']})"
        return output

    metadata = raw_papers["metadata"]
    papers_fetched = raw_papers["papers"]

    preprints = [paper for paper in papers_fetched if not paper["is_paper"]]
    papers = [paper for paper in papers_fetched if paper["is_paper"]]

    preprints_text = "".join([format_paper(paper) + "\n" for paper in preprints])
    papers_text = "".join([format_paper(paper) + "\n" for paper in papers])

    start_date_suffix = f" since {metadata['since']}" if metadata.get("since") else ""

    output = ""
    output += f"📅 Found {len(papers_fetched)} new preprints and papers{start_date_suffix}.\n\n"
    output += f"📄 *Preprints*:\n{preprints_text}\n" if preprints else ""
    output += f"📝 *Papers*:\n{papers_text}\n" if papers else ""

    return output
