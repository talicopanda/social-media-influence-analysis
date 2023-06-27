from typing import List, Sequence
import warnings
import pandas as pd

warnings.simplefilter(action='ignore', category=FutureWarning)
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from sklearn.preprocessing import MinMaxScaler, StandardScaler, MaxAbsScaler


def gc_score_for_lag(indep_series: Sequence[int],
                     dep_series: Sequence[int], lag: int,
                     test: str = "ssr_chi2test", verbose: bool = False) -> float:
    """Return the p value for Granger causality test for <indep_series>
     and <dep_series> with <lag>.
     """
    granger_test = grangercausalitytests(pd.DataFrame({
        "y": dep_series,
        "x": indep_series
    }), maxlag=[lag], verbose=verbose)
    return granger_test[lag][0][test][1]


def gc_score_for_lags(indep_series: Sequence[int],
                      dep_series: Sequence[int], lags: List[int],
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


def is_stationary(x: Sequence[int], sig_level: float = 0.05) -> bool:
    test_result = adfuller(x)
    p_val = test_result[1]
    return p_val < sig_level
