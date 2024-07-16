import argparse
import logging

import paperbot

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)

TEMPLATE_QUERIES_DIR = "queries/"


def fetch_papers(title: str):
    """Fetch papers."""
    logging.info("Fetching papers...")
    reference_paper, similar_papers = paperbot.fetch_similar_papers(title)
    logging.info("Done fetching papers.")

    overview = paperbot.format_query_papers(similar_papers, None, format_type="plain")
    logging.info(overview)

    n_papers = len(similar_papers)
    logging.info(f"Number of papers: {n_papers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("title", type=str, help="Title of reference paper")

    args = parser.parse_args()

    fetch_papers(args.title)
