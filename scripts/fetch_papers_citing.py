import argparse
import logging

import paperbot

logging.basicConfig(level=logging.INFO)


def fetch_papers(title: str, limit: int):
    """Fetch papers."""
    logging.info("Fetching papers...")
    paper, citing_papers = paperbot.fetch_papers_citing(title, limit)
    logging.info("Done fetching papers.")

    text = paperbot.format_papers_citing(paper, citing_papers, title, format_type="plain")
    logging.info(text)

    n_papers = len(citing_papers)
    logging.info(f"Number of papers: {n_papers}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("title", type=str, help="Title of paper")
    parser.add_argument("--limit", type=str, help="Max number of papers to fetch", default=15)

    args = parser.parse_args()

    fetch_papers(args.title, args.limit)
