import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from sklearn.metrics.pairwise import cosine_similarity

from typing import List, Sequence

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)


def gc_score_for_lag(indep_series: Sequence, dep_series: Sequence, lag: int,
                     test: str = "ssr_chi2test", verbose: bool = False) \
        -> float:
    """Return the p value for Granger causality test for <indep_series>
     and <dep_series> with <lag>.
     """
    granger_test = grangercausalitytests(pd.DataFrame({
        "y": dep_series,
        "x": indep_series
    }), maxlag=[lag], verbose=verbose)
    return granger_test[lag][0][test][1]


def gc_score_for_lags(indep_series: Sequence, dep_series: Sequence, lags: List[int],
                      test: str = "ssr_chi2test", verbose: bool = False) \
        -> List[float]:
    """Return a list of p values for Granger causality test for <indep_series>
    and <dep_series> with <lag>.
    """
    granger_test = grangercausalitytests(pd.DataFrame({
        "y": dep_series,
        "x": indep_series
    }), maxlag=lags, verbose=verbose)
    p_value_list = [granger_test[lag][0][test][1] for lag in lags]
    return p_value_list


def is_stationary(x: Sequence, sig_level: float = 0.05) -> bool:
    test_result = adfuller(x)
    p_val = test_result[1]
    return p_val < sig_level


def cos_similarity(seq1: Sequence, seq2:Sequence) -> float:
    """Return the cosine similarity between two sequence.
    """
    # Convert sequences to numpy arrays
    vec1 = np.array(seq1)
    vec2 = np.array(seq2)

    # Reshape arrays to be 2-dimensional
    vec1 = vec1.reshape(1, -1)
    vec2 = vec2.reshape(1, -1)

    # Calculate cosine similarity
    similarity = cosine_similarity(vec1, vec2)[0, 0]

    return similarity
