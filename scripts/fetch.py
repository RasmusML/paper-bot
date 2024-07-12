import argparse
import datetime
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

    papers = paperbot.prepare_papers(papers)
    overview = paperbot.format_paper_overview(papers, since, format_type="plain")

    logging.info(overview)

    n_papers = len(papers)
    logging.info(f"Number of papers: {n_papers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("query_file", type=str, help="Filename of a query in the directory \'queries/\'")
    parser.add_argument("--since", type=str, help="Start date", default="2022-01-01")
    parser.add_argument("--until", type=str, help="End date")

    args = parser.parse_args()

    template_queries = paperbot.read_queries_from_dir(TEMPLATE_QUERIES_DIR)

    try:
        query = template_queries[args.query_file]
    except KeyError as err:
        raise ValueError(f"Query file not found: \'{args.query_file}\'") from err

    since = datetime.date.fromisoformat(args.since) if args.since else None
    until = datetime.date.fromisoformat(args.until) if args.until else None

    fetch_papers(query, since, until)
