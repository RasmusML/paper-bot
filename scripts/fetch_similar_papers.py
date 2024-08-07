import argparse
import logging

import paperbot

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def fetch_papers(title: str, limit: int):
    """Fetch papers."""
    logging.info("Fetching papers...")
    paper, similar_papers = paperbot.fetch_similar_papers(title, limit)
    logging.info("Done fetching papers.")

    text = paperbot.format_similar_papers(paper, similar_papers, title, format_type="plain")
    logging.info(text)

    n_papers = len(similar_papers)
    logging.info(f"Number of papers: {n_papers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("title", type=str, help="Title of paper")
    parser.add_argument("--limit", type=str, help="Max number of papers to fetch", default=15)

    args = parser.parse_args()

    fetch_papers(args.title, args.limit)
