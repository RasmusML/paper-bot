import logging
import uuid
from pathlib import Path


def read_queries_from_dir(dir: str) -> dict[str, str]:
    """Read queries from text files in a directory and store them in a dictionary."""
    paths = Path(dir)

    queries = {}
    for path in paths.glob("*.txt"):
        with open(path) as f:
            query = f.read()

        filename_no_ext = path.stem
        queries[filename_no_ext] = query

    return queries


def init_bot_logger(logger: logging.Logger, filename: str = None, level=logging.DEBUG):
    """Initialize logging for the provided logger."""
    logger.setLevel(level)

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(console_handler)

        if filename:
            path = Path(filename)
            path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(filename, encoding="utf-8")
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)

            logger.addHandler(file_handler)


def create_uuid() -> str:
    """Create a UUID."""
    return uuid.uuid4().hex
