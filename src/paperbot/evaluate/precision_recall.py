"""Implementation of the precision and recall metric for generative models.

[1] "Improved Precision and Recall Metric for Assessing Generative Models"
    by Kynkäänniemi et al. (2018)

"""

import numpy as np
from scipy.spatial.distance import cdist


def precision(xs_gen, xs_data, k=3, q=1):
    """Precision."""
    return _metric(xs_gen, xs_data, k, q)


def recall(xs_gen, xs_data, k=3, q=1):
    """Recall."""
    return _metric(xs_data, xs_gen, k, q)


def r_score(xs, mf_xs, k=3, q=0.5):
    """Manifold sample score."""
    mf_dist = _pairwise_dist(mf_xs, mf_xs)
    idx_k = _k_argmin(mf_dist, k)
    r_k = mf_dist[np.arange(mf_xs.shape[0]), idx_k]

    m_q = r_k < np.quantile(r_k, q)
    mf_xs2, r_k2 = mf_xs[m_q, :], r_k[m_q]

    q_dist = _pairwise_dist(xs, mf_xs2)

    d = np.true_divide(r_k2, q_dist, out=np.full_like(q_dist, 1e8), where=q_dist != 0)
    s = np.max(d, axis=1)

    return s, r_k, m_q


def p_score(xs, mf_xs, k=3, q=0.5):
    """Probability that sample is on manifold."""
    s, r_k, m_q = r_score(xs, mf_xs, k, q)
    p = _sigmoid(np.log(s))
    return p, r_k, m_q


def _metric(xs, mf_xs, k=3, q=1):
    r, _, _ = r_score(xs, mf_xs, k, q)
    m_r = r >= 1
    return np.sum(m_r) / len(m_r), m_r


def _pairwise_dist(xs, ys):
    return cdist(xs, ys, metric="euclidean")


def _k_argmin(vs, k):
    return np.argsort(vs, axis=1)[:, k]


def _sigmoid(x):
    return 1 / (1 + np.exp(-x))
