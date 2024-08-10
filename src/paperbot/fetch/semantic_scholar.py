from typing import Any, Literal

import requests
import requests.adapters
from requests.exceptions import HTTPError


def fetch_similar_papers_from_id(
    paper_id: str,
    from_pool: Literal["recent", "all-cs"] = None,
    limit: int = None,
    fields: str = None,
) -> dict[str, Any]:
    """Fetch papers similar to the paper with id `paper id`.

    References
    ----------
    https://api.semanticscholar.org/api-docs/recommendations#tag/Paper-Recommendations/operation/get_papers_for_paper

    """
    res = requests.get(
        f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}",
        params={
            "from": from_pool,
            "limit": limit,
            "fields": fields,
        },
    )
    res.raise_for_status()
    return res.json()


def fetch_paper_from_title(
    title: str,
    fields: str = None,
) -> dict[str, Any] | None:
    """Fetch a single paper based on title.

    References
    ----------
    https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_paper_title_search

    """
    try:
        res = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search/match",
            params={
                "query": title,
                "fields": fields,
            },
        )
        res.raise_for_status()

    except HTTPError as err:
        if _is_no_paper_matching_title(err.response):
            return None
        raise err

    return res.json()


def fetch_papers_from_query(
    query: str,
    fields: str = None,
    publication_date_or_year: str = None,
    publication_types: str = None,
    token: str = None,
) -> dict[str, Any]:
    """Fetch papers based on search query.

    References
    ----------
    https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_paper_bulk_search

    """
    res = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search/bulk",
        params={
            "query": query,
            "fields": fields,
            "publicationDateOrYear": publication_date_or_year,
            "publicationTypes": publication_types,
            "token": token,
        },
    )
    res.raise_for_status()
    return res.json()


def fetch_papers_citing(paper_id: str, limit: int = None, fields: str = None) -> dict[str, Any]:
    """Fetch papers citing the paper with title `title`.

    References
    ----------
    https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_get_paper_citations

    """
    res = requests.get(
        f"https://api.semanticscholar.org/graph/v1/paper/{paper_id}/citations",
        params={  # type: ignore # @TODO: why?
            "limit": limit,
            "fields": fields,
        },
    )
    res.raise_for_status()
    return res.json()


def _is_no_paper_matching_title(response: requests.Response) -> bool:
    status_code = response.status_code
    content = response.json()
    return (status_code == 404) and (content.get("error") == "Title match not found")
