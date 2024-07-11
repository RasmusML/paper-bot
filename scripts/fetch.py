import argparse
import datetime
import json
import logging

import paperbot

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

TEMPLATE_QUERIES_DIR = "queries/"


def fetch_papers(query: str, since: datetime.date, until: datetime.date):
    """Fetch papers."""
    logging.info("Fetching papers...")
    papers = paperbot.fetch_papers(
        query=query,
        since=since,
        until=until,
    )
    logging.info("Done fetching papers.")

    output = json.dumps(papers, indent=2)
    logging.info(f"Output:\n{output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query_file", type=str, help="Path to query file")
    parser.add_argument("--since", type=str, help="Date since")
    parser.add_argument("--until", type=str, help="Date until")

    args = parser.parse_args()

    template_queries = paperbot.read_queries_from_dir(TEMPLATE_QUERIES_DIR)
    query = template_queries.get(args.query_file)

    if not query:
        raise ValueError(f"Query file not found: {args.query_file}")

    since = datetime.date.fromisoformat(args.since) if args.since else None
    until = datetime.date.fromisoformat(args.until) if args.until else None

    fetch_papers(query, since, until)
