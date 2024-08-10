import argparse
import datetime
import logging
import os

import paperbot

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

TEMPLATE_QUERIES_DIR = "queries/"


def fetch_papers(query: str, since: datetime.date, until: datetime.date, limit: int, save_titles: bool):
    """Fetch papers."""
    logging.info("Fetching papers...")
    papers = paperbot.fetch_papers_from_query(
        query=query,
        since=since,
        until=until,
        limit=limit,
    )
    logging.info("Done fetching papers.")

    text = paperbot.format_query_papers(query, papers, since, format_type="plain")
    logging.info(text)

    n_papers = len(papers)
    logging.info(f"Number of papers: {n_papers}")

    if save_titles:
        path = "outputs/query.txt"
        os.makedirs(os.path.dirname(path), exist_ok=True)

        titles = [paper["title"] for paper in papers]
        content = "".join([title + "\n" for title in titles])

        with open(path, "w") as file:
            file.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "query_file",
        type=str,
        help="Filename of a query in the directory 'queries/' (without file extension)",
    )
    parser.add_argument("--since", type=str, help="Start date", default="2022-01-01")
    parser.add_argument("--until", type=str, help="End date")
    parser.add_argument("--limit", type=int, help="Max number of papers to fetch")
    parser.add_argument("--save", action="store_true", help="Save papers to a file")

    args = parser.parse_args()

    template_queries = paperbot.read_queries_from_dir(TEMPLATE_QUERIES_DIR)

    try:
        query = template_queries[args.query_file]
    except KeyError as err:
        raise ValueError(f"Query file not found: '{args.query_file}'") from err

    since = datetime.date.fromisoformat(args.since) if args.since else None
    until = datetime.date.fromisoformat(args.until) if args.until else None
    limit = args.limit
    save_titles = args.save

    fetch_papers(query, since, until, limit, save_titles)
