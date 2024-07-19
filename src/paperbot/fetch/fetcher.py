import datetime
from typing import Any

import paperbot.fetch.semantic_scholar as ss


def fetch_similar_papers(title: str, limit=5) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Fetch similar papers."""
    fields = "paperId,title,url,externalIds"
    raw_paper = ss.fetch_paper_from_title(title, fields)

    if ("error" in raw_paper) and (raw_paper["error"] == "Title match not found"):
        return None, None

    paper = _extract_paper_data(raw_paper["data"][0])

    fields = "paperId,title,url,externalIds,publicationTypes,publicationDate,year"
    raw_similar_papers = ss.fetch_similar_papers_from_id(
        paper["id"],
        from_pool="all-cs",
        limit=limit,
        fields=fields,
    )

    similar_papers = [_extract_paper_data(paper) for paper in raw_similar_papers["recommendedPapers"]]
    similar_papers = _remove_duplicate_papers(similar_papers)

    return paper, similar_papers


def fetch_papers_from_query(
    query: str,
    since: datetime.date = None,
    until: datetime.date = None,
    limit: int = None,
) -> list[dict[str, Any]]:
    """Fetch papers."""
    fields = "title,url,externalIds,publicationTypes,publicationDate,year"
    publication_period = _format_publication_period(since, until)
    raw_papers = ss.fetch_papers_from_query(query, fields, publication_period)

    if "error" in raw_papers:
        raise RuntimeError("Bad query!")

    papers = [_extract_paper_data(paper) for paper in raw_papers["data"]]
    papers = _remove_duplicate_papers(papers)
    papers = _sort_papers_by_date(papers)
    papers = _filter_by_paper_limit(papers, limit) if limit else papers

    return papers


def _filter_by_paper_limit(papers: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    return papers[-limit:]


def _remove_duplicate_papers(papers: list[dict[str, Any]], key: str = "id") -> list[dict[str, Any]]:
    unique_papers = []
    unique_ids = set()

    for paper in papers:
        if paper[key] not in unique_ids:
            unique_papers.append(paper)
            unique_ids.add(paper[key])

    return unique_papers


def _extract_paper_data(paper: dict[str, Any]) -> dict[str, Any]:
    id = paper.get("paperId")
    title = paper.get("title")
    semantic_scholar_url = paper.get("url")
    publication_types = paper.get("publicationTypes")
    publication_date = paper.get("publicationDate")
    year = paper.get("year")

    doi = None
    if "externalIds" in paper:
        doi = paper["externalIds"].get("DOI")

    if (not publication_date) and year:
        publication_date = f"{year}-01-01"

    url = _get_url_from_doi(doi) if doi else semantic_scholar_url
    is_paper = "JournalArticle" in publication_types if publication_types else False

    full_result = {
        "id": id,
        "title": title,
        "url": url,
        "publication_date": publication_date,
        "is_paper": is_paper,
    }

    result = {k: v for k, v in full_result.items() if v is not None}

    return result


def _get_date_format(date: datetime.date) -> str:
    return date.strftime("%Y-%m-%d")


def _format_publication_period(since: datetime.date, until: datetime.date) -> str | None:
    if (since is None) and (until is None):
        return None

    since_str = _get_date_format(since) if since is not None else ""
    until_str = _get_date_format(until) if until is not None else ""

    return f"{since_str}:{until_str}"


def _sort_papers_by_date(papers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return sorted(papers, key=lambda paper: datetime.datetime.strptime(paper["publication_date"], "%Y-%m-%d"))


def _get_url_from_doi(doi_id: str) -> str:
    return f"https://doi.org/{doi_id}"
