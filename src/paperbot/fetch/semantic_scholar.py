from typing import Any, Literal

import requests


def fetch_similar_papers_from_id(
    paper_id: str,
    from_pool: Literal["recent", "all-cs"] = None,
    limit: int = None,
    fields: str = None,
) -> dict[str, Any]:
    """Fetch similar papers based on reference paper id.

    References
    ----------
    https://api.semanticscholar.org/api-docs/recommendations#tag/Paper-Recommendations/operation/get_papers_for_paper

    """
    req = requests.get(
        f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}",
        params={
            "from": from_pool,
            "limit": limit,
            "fields": fields,
        },
    )
    return req.json()


def fetch_paper_from_title(
    title: str,
    fields: str = None,
) -> dict[str, Any]:
    """Fetch a single paper based on title.

    References
    ----------
    https://api.semanticscholar.org/api-docs/graph#tag/Paper-Data/operation/get_graph_paper_title_search

    """
    req = requests.get(
        "https://api.semanticscholar.org/graph/v1/paper/search/match",
        params={
            "query": title,
            "fields": fields,
        },
    )
    return req.json()


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
