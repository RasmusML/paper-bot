import datetime
import logging
from pathlib import Path
from typing import Literal

import requests

logger = logging.getLogger(__name__)


def _search_bulk(
    query: str, fields: str = None, publicationDateOrYear: str = None, publicationTypes: str = None, token: str = None
) -> dict:
    # Reference: https://api.semanticscholar.org/api-docs/graph
    req = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
        params={
            "query": query,
            "fields": fields,
            "publicationDateOrYear": publicationDateOrYear,
            "publicationTypes": publicationTypes,
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
    publication_period = _format_publication_period(since, until)
    fields = "title,url,externalIds,publicationTypes,publicationDate,year"
    res = _search_bulk(query, fields, publication_period)
    return res


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
    # @TODO: handle total == 0

    papers = [_extract_paper_data(paper) for paper in raw_papers["data"]]
    papers = sorted(papers, key=lambda paper: datetime.datetime.strptime(paper["publication_date"], "%Y-%m-%d"))

    return papers


def prepare_papers(raw_papers: dict) -> list[dict]:
    """Prepare the fetched papers for further processing."""
    return _preprocess_papers(raw_papers)


# @TODO: https://discordpy.readthedocs.io/en/stable/faq.html#coroutines
# https://requests.readthedocs.io/en/latest/user/advanced/#session-objects


def format_paper_overview(
    papers: list[dict], since: datetime.date, format_type: Literal["plain", "slack", "discord"] = "plain"
) -> str:
    """Generate an overview of the fetched papers."""
    FORMATTERS = {
        "plain": PlainFormatter(),
        "slack": SlackFormatter(),
        "discord": DiscordFormatter(),
    }

    if format_type not in FORMATTERS:
        raise ValueError(f"Formatter {format_type} is not supported.")

    formatter = FORMATTERS[format_type]

    preprints = [paper for paper in papers if not paper["is_paper"]]
    papers = [paper for paper in papers if paper["is_paper"]]

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
    url = paper["url"]

    link = formatter.linkify(title, url)
    item = formatter.itemize(link)
    return item


def _get_url_from_doi(doi_id: str):
    return f"https://doi.org/{doi_id}"


class Formatter:
    def linkify(self, text: str, url: str) -> str:
        """Linkify a text with a URL."""
        raise NotImplementedError

    def itemize(self, text: str) -> str:
        """Itemize a text."""
        raise NotImplementedError

    def bold(self, text: str) -> str:
        """Make text bold."""
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


def read_queries_from_dir(queries_dir: str) -> dict[str, str]:
    """Read queries from text files in a directory and store them in a dictionary."""
    queries_dir_pth = Path(queries_dir)

    queries = {}
    for query_pth in queries_dir_pth.glob("*.txt"):
        with open(query_pth) as f:
            query = f.read()

        filename = query_pth.stem
        queries[filename] = query

    return queries
