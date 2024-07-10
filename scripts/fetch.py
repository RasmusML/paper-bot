import json
import logging
from datetime import datetime
from pathlib import Path

import paperbot
import yaml

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def load_config(config_path: str) -> dict:
    config_pth = Path(config_path)

    with open(config_pth) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)

    query_pth = config_pth.parent / config["query_path"]

    with open(query_pth) as f:
        query = f.read()

    config["query"] = query

    return config


def fetch_papers():
    config = load_config("./configs/config.yaml")

    query = config["query"]
    since = config.get("since")
    until = config.get("until")

    logging.info("Fetching papers...")
    papers = paperbot.fetch_papers(
        query=query,
        since=since,
        until=until,
    )
    logging.info("Done fetching papers.")

    print(json.dumps(papers, indent=2))


if __name__ == "__main__":
    fetch_papers()
