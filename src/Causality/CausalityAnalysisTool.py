import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import grangercausalitytests, adfuller, \
    InfeasibleTestError
import statsmodels.api as sm
from sklearn.metrics.pairwise import cosine_similarity

from typing import List, Sequence, Tuple

import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)


def gc_score_for_lag(indep_series: Sequence, dep_series: Sequence, lag: int,
                     test: str = "ssr_chi2test", verbose: bool = False) \
        -> float:
    """Return the p value for Granger causality test for <indep_series>
     and <dep_series> with <lag>.
     """
    if lag > 0:
        granger_test = grangercausalitytests(pd.DataFrame({
            "y": dep_series,
            "x": indep_series
        }), maxlag=[lag], verbose=verbose)
        return granger_test[lag][0][test][1]
    elif lag < 0:
        granger_test = grangercausalitytests(pd.DataFrame({
            "y": indep_series,
            "x": dep_series
        }), maxlag=[-lag], verbose=verbose)
        return granger_test[-lag][0][test][1]
    else:
        return 1


def gc_score_for_lags(indep_series: Sequence, dep_series: Sequence,
                      lags: List[int],
                      test: str = "ssr_chi2test", verbose: bool = False) \
        -> List[float]:
    """Return a list of p values for Granger causality test for <indep_series>
    and <dep_series> with <lag>.
    """
    result = []
    for lag in lags:
        try:
            p_val = gc_score_for_lag(indep_series, dep_series, lag, test,
                                     verbose)
        except InfeasibleTestError:
            p_val = 1
        result.append(p_val)
    return result


def is_stationary(x: Sequence, sig_level: float = 0.05) -> bool:
    test_result = adfuller(x)
    p_val = test_result[1]
    return p_val < sig_level


def cos_similarity(seq1: Sequence, seq2: Sequence) -> float:
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


def cs_for_lag(indep_series: Sequence, dep_series: Sequence, lag: int) -> float:
    assert len(indep_series) == len(dep_series)
    if lag > 0:
        return cos_similarity(indep_series[:-lag], dep_series[lag:])
    elif lag < 0:
        return cos_similarity(indep_series[-lag:], dep_series[:lag])
    else:
        return cos_similarity(indep_series, dep_series)


def cs_for_lags(indep_series: Sequence, dep_series: Sequence,
                lags: List[int]) -> List[float]:
    """
    Precondition: min(lags) < 0 and max(lags) > 0
    """
    min_lag = min(lags)
    max_lag = max(lags)
    indep_slice = indep_series[-min_lag:-max_lag]

    result = []
    for lag in lags:
        if max_lag == lag:
            dep_slice = dep_series[- min_lag + lag:]
        else:
            dep_slice = dep_series[- min_lag + lag: - max_lag + lag]
        assert len(dep_slice) == len(indep_slice)
        result.append(cos_similarity(indep_slice, dep_slice))
    return result


def ols_slope(indep_series: Sequence, dep_series: Sequence) -> \
        Tuple[float, Tuple[float, float]]:
    """Return p-value, lower bound, and upper bound of confidence interval with
    significant level = 0.05.
    """
    # independent variable preprocessing
    indep_series = sm.add_constant(indep_series)

    # model fit
    model = sm.OLS(dep_series, indep_series).fit()
    slope = model.params[1]
    conf_int = tuple(model.conf_int(alpha=0.05)[1])
    return slope, conf_int


def lr_for_lag(indep_series: Sequence, dep_series: Sequence, lag: int) -> \
        Tuple[float, Tuple[float, float]]:
    """Return p-value, lower bound, and upper bound of confidence interval.
    """
    if _list_depth(indep_series) == 1:
        if lag > 0:
            return ols_slope(np.array([indep_series[:-lag], dep_series[:-lag]]).T, dep_series[lag:])
        elif lag < 0:
            return ols_slope(np.array([dep_series[:lag], indep_series[:lag]]).T, indep_series[-lag:])
        else:
            return 0, (0, 0)
    elif _list_depth(indep_series) == 2:
        indep_input = []
        dep_indep = []
        dep_input = []
        if lag > 0:
            # build input list
            for indep_list in indep_series:
                indep_input.extend(indep_list[:-lag])
            for dep_list in dep_series:
                dep_indep.extend(dep_list[:-lag])
                dep_input.extend(dep_list[lag:])

            return ols_slope(np.array([indep_input, dep_indep]).T, dep_input)
        elif lag < 0:
            # build input list
            for indep_list in indep_series:
                indep_input.extend(indep_list[-lag:])
                dep_indep.extend(indep_list[:lag])
            for dep_list in dep_series:
                dep_input.extend(dep_list[:lag])

            return ols_slope(dep_input, indep_input)
        else:
            return 0, (0, 0)


def lr_for_lags(indep_series: Sequence, dep_series: Sequence,
                lags: List[int]) -> Tuple[List[float], List[Tuple[float, float]]]:
    slope_list = []
    conf_int_list = []
    for lag in lags:
        slope, conf_int = lr_for_lag(indep_series, dep_series, lag)
        slope_list.append(slope)
        conf_int_list.append(conf_int)
    return slope_list, conf_int_list


def _list_depth(lst: Sequence) -> int:
    """Return the depth of lst. Assume the input list has at least one element,
    and the depth is uniform across all sublist.
    """
    sub = lst[0]
    if isinstance(sub, list):
        return _list_depth(sub) + 1
    return 1
