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
