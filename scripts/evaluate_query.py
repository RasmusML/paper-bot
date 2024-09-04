import argparse
import logging

import matplotlib.pyplot as plt
import numpy as np
import requests
from sklearn.decomposition import PCA
from tqdm import tqdm

import paperbot as pb
from paperbot.evaluate import Specter2, p_score, precision, recall

logger = logging.getLogger(__name__)

logging.basicConfig(level=logging.INFO)


def _fetch_papers(titles, max_attempts=5):
    papers = []
    for title in tqdm(titles):
        for k in range(max_attempts):
            try:
                paper = pb.fetch_single_paper(title)
                papers += [paper]
                break
            except requests.HTTPError as err:
                attempt = k + 1
                if attempt == max_attempts:
                    error_msg = f"Failed to fetch a paper after doing {max_attempts} attempts. Consider increasing `max_attempts`."
                    raise RuntimeError(error_msg) from err

    return papers


def _print_result(d):
    titles = d["titles"]
    pcs = d.get("pca")
    p_s = d.get("p_scores")
    has_abstract = d.get("has_abstract")

    for i in range(len(titles)):
        t_title = titles[i]
        t_embeddings = f" (PCs=[{pcs[i][0]:.2f}, {pcs[i][1]:.2f}])" if pcs is not None else ""
        t_p_s = f" (p={p_s[i]:.2f})" if p_s is not None else ""
        t_abstract = " (❌ abstract)" if not has_abstract[i] else ""

        print(f"- {t_title}{t_embeddings}{t_p_s}{t_abstract}")


def evaluate_query(
    query_titles: np.ndarray,
    positives_titles: np.ndarray,
    max_tokens: int,
    k: float,
    q: float,
    max_attempts_to_fetch: int,
):
    """Fetch papers."""
    logging.info("Fetching papers...")

    logging.info(f"Positive papers: {len(positives_titles)}")
    logging.info(f"Query papers: {len(query_titles)}")

    logging.info("Fetching positves.")
    positives = _fetch_papers(positives_titles, max_attempts=max_attempts_to_fetch)

    positives_with_abstract = np.array(["abstract" in p for p in positives])
    p_positives_with_abstract = np.sum(positives_with_abstract) / len(positives) * 100
    logging.info(f"{p_positives_with_abstract:.0f}% positives contain abstract")

    logging.info("Fetching queries.")
    query = _fetch_papers(query_titles, max_attempts=max_attempts_to_fetch)

    query_with_abstract = np.array(["abstract" in p for p in query])
    p_query_with_abstract = np.sum(query_with_abstract) / len(query) * 100
    logging.info(f"{p_query_with_abstract:.0f}% queries contain abstract")

    model = Specter2()
    positives_embeddings = model.get_embeddings(positives, max_length=max_tokens)
    query_embeddings = model.get_embeddings(query, max_length=max_tokens)

    # Compute precision (true positives) and recall
    positives_best, _ = precision(positives_embeddings, positives_embeddings, k=k, q=q)

    precision_query, precision_mask = precision(query_embeddings, positives_embeddings, k=k, q=q)
    recall_query, _ = recall(query_embeddings, positives_embeddings, k=k, q=q)

    print(f"\nPositive self-containing: {positives_best:.2f}")
    print(f"Precision: {precision_query:.2f}")
    print(f"Recall: {recall_query:.2f}")

    # Print true positives and false positives
    p_scores, _, positives_mask = p_score(query_embeddings, positives_embeddings, k=k, q=q)

    combined_embeddings = np.concatenate((positives_embeddings, query_embeddings), axis=0)
    combined_embeddings = np.unique(combined_embeddings, axis=0, return_index=False)

    pca = PCA(n_components=10)
    pca.fit(combined_embeddings)

    positives_embeddings_pca = pca.transform(positives_embeddings)
    query_embeddings_pca = pca.transform(query_embeddings)

    query_tp = {
        "titles": query_titles[precision_mask],
        "pca": query_embeddings_pca[precision_mask],
        "p_scores": p_scores[precision_mask],
        "has_abstract": query_with_abstract[precision_mask],
    }

    print("\n*True positives*")
    _print_result(query_tp)

    query_fp = {
        "titles": query_titles[~precision_mask],
        "pca": query_embeddings_pca[~precision_mask],
        "p_scores": p_scores[~precision_mask],
        "has_abstract": query_with_abstract[~precision_mask],
    }

    print("\n*False positives*")
    _print_result(query_fp)

    # Plot variance explained
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(np.arange(pca.explained_variance_ratio_.shape[0]) + 1, np.cumsum(pca.explained_variance_ratio_), marker="o")
    ax.set_title("Variance explained")
    ax.set_xlabel("Number of components")
    ax.set_ylabel("Cumulative explained variance")
    ax.set_xticks(np.arange(pca.explained_variance_ratio_.shape[0]) + 1)
    ax.grid()

    plt.show()

    # Plot PCs
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(
        positives_embeddings_pca[positives_mask, 0],
        positives_embeddings_pca[positives_mask, 1],
        c="gray",
        label="positives used",
    )
    ax.scatter(
        positives_embeddings_pca[~positives_mask, 0],
        positives_embeddings_pca[~positives_mask, 1],
        c="lightgray",
        label="positives ignored",
    )

    ax.scatter(query_tp["pca"][:, 0], query_tp["pca"][:, 1], c="lime", label="query inside")
    ax.scatter(query_fp["pca"][:, 0], query_fp["pca"][:, 1], c="red", label="query outside")

    ax.set_xlabel("PC1")
    ax.set_ylabel("PC2")
    ax.legend()

    plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--positive_list",
        type=str,
        help="Path to text file with (newline seperated) paper titles constituting 'good' papers",
        default="papers/amp.txt",
    )
    parser.add_argument(
        "--query_list",
        type=str,
        help="Path to text file with (newline seperated) paper titles from query to be evaluated.",
        default="outputs/query.txt",
    )

    parser.add_argument(
        "--max_tokens",
        type=int,
        help="Max number of tokens in the title + abstract concatenated.",
        default=64,
        choices=np.arange(512) + 1,
    )

    parser.add_argument(
        "--k",
        type=int,
        help="kth nearest used for precision/recall distance computation.",
        default=3,
    )

    parser.add_argument(
        "--q",
        type=float,
        help="Quantile to filter the positive list with for precision/recall computation.",
        default=0.9,
    )

    parser.add_argument(
        "--max_fetch_attempts",
        type=int,
        help="Number of times to attempt to fetch a paper.",
        default=5,
    )

    args = parser.parse_args()

    with open(args.positive_list) as f:
        pos_titles = f.readlines()
        positives_titles = np.array([title.strip() for title in pos_titles])

    with open(args.query_list) as f:
        q_titles = f.readlines()
        query_titles = np.array([title.strip() for title in q_titles])

    evaluate_query(
        query_titles,
        positives_titles,
        args.max_tokens,
        args.k,
        args.q,
        args.max_fetch_attempts,
    )
