import datetime
import logging
from pathlib import Path
from typing import Any, Literal

import requests

import paperbot.formatter.slack as slk
import paperbot.formatter.text as txt

logger = logging.getLogger(__name__)


def _search_bulk(
    query: str, fields: str = None, publication_date_or_year: str = None, publication_types: str = None, token: str = None
) -> dict:
    # Reference: https://api.semanticscholar.org/api-docs/graph
    req = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
        params={
            "query": query,
            "fields": fields,
            "publicationDateOrYear": publication_date_or_year,
            "publicationTypes": publication_types,
            "token": token,
        },
    )
    return req.json()


def fetch_papers(
    query: str,
    since: datetime.date = None,
    until: datetime.date = None,
):
    """Fetch papers."""
    fields = "title,url,externalIds,publicationTypes,publicationDate,year"
    publication_period = _format_publication_period(since, until)
    result = _search_bulk(query, fields, publication_period)
    return result


def _get_date_format(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


def _format_publication_period(since: datetime.date, until: datetime.date) -> str | None:
    if (since is None) and (until is None):
        return None

    since_str = _get_date_format(since) if since is not None else ""
    until_str = _get_date_format(until) if until is not None else ""

    return f"{since_str}:{until_str}"


def _extract_paper_data(paper: dict) -> dict:
    title = paper["title"]
    doi = paper["externalIds"].get("DOI")
    semanticscholar_url = paper["url"]
    publication_type = paper["publicationTypes"]
    publication_date = paper["publicationDate"]
    year = paper["year"]

    if publication_date is None:
        publication_date = f"{year}-01-01"

    url = semanticscholar_url if doi is None else _get_url_from_doi(doi)

    return {
        "title": title,
        "url": url,
        "publication_type": publication_type,
        "publication_date": publication_date,
        "is_paper": "JournalArticle" in publication_type if publication_type else False,
    }


def _preprocess_papers(raw_papers: dict) -> list[dict]:
    """Prepare the fetched papers for further processing."""
    papers = [_extract_paper_data(paper) for paper in raw_papers["data"]]
    papers = sorted(papers, key=lambda paper: datetime.datetime.strptime(paper["publication_date"], "%Y-%m-%d"))
    return papers


def prepare_papers(raw_papers: dict) -> list[dict]:
    """Prepare the fetched papers for further processing."""
    return _preprocess_papers(raw_papers)


def _get_url_from_doi(doi_id: str) -> str:
    return f"https://doi.org/{doi_id}"


FORMATTER = {
    "plain": txt.format_paper_overview_plain,
    "slack": txt.format_paper_overview_slack,
    "discord": txt.format_paper_overview_discord,
    "slack-fancy": slk.format_paper_overview,
}


def format_paper_overview(
    papers: list[dict], since: datetime.date, format_type: Literal["plain", "slack", "discord", "slack-fancy"] = "plain"
) -> str | list[Any]:
    """Format the fetched papers."""
    fmt = FORMATTER.get(format_type)

    if fmt is None:
        raise ValueError(f"Invalid format type: {format_type}")

    return fmt(papers, since)  # type: ignore


def read_queries_from_dir(dir: str) -> dict[str, str]:
    """Read queries from text files in a directory and store them in a dictionary."""
    query_paths = Path(dir)

    queries = {}
    for path in query_paths.glob("*.txt"):
        with open(path) as f:
            query = f.read()

        filename = path.stem
        queries[filename] = query

    return queries
