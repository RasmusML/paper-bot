import argparse
import logging

import paperbot

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

TEMPLATE_QUERIES_DIR = "queries/"


def fetch_papers(title: str, limit: int):
    """Fetch papers."""
    logging.info("Fetching papers...")
    reference_paper, similar_papers = paperbot.fetch_similar_papers(title, limit)
    logging.info("Done fetching papers.")

    outpput = paperbot.format_similar_papers(reference_paper, similar_papers, title, format_type="plain")
    logging.info(outpput)

    n_papers = len(similar_papers)
    logging.info(f"Number of papers: {n_papers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("title", type=str, help="Title of reference paper")
    parser.add_argument("--limit", type=str, help="Max number of papers to fetch", default=15)

    args = parser.parse_args()

    fetch_papers(args.title, args.limit)
