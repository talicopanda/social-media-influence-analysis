from typing import List
import warnings
import pandas as pd
import numpy as np

warnings.simplefilter(action='ignore', category=FutureWarning)
from statsmodels.tsa.stattools import grangercausalitytests, adfuller
from sklearn.preprocessing import MinMaxScaler, StandardScaler, MaxAbsScaler


def gc_score_for_lag(indep_series: List[int],
                     dep_series: List[int], lag: int,
                     test: str = "ssr_chi2test", verbose: bool = False) -> float:
    """Return the p value for Granger causality test for <indep_series>
     and <dep_series> with <lag>.
     """
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": dep_series,
        "y": indep_series
    }), maxlag=[lag], verbose=verbose)
    return granger_test[lag][0][test][1]


def gc_score_for_lags(indep_series: List[int],
                      dep_series: List[int], lags: List[int],
                      test: str = "ssr_chi2test", verbose: bool = False) -> List[float]:
    """Return a list of p values for Granger causality test for <indep_series>
    and <dep_series> with <lag>.
    """
    # indep_series = MaxAbsScaler().fit_transform(np.array(indep_series).reshape(-1, 1)).reshape(-1)
    # dep_series = MaxAbsScaler().fit_transform(np.array(dep_series).reshape(-1, 1)).reshape(-1)
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": dep_series,
        "y": indep_series
    }), maxlag=lags, verbose=verbose)
    p_value_list = [granger_test[lag][0][test][1] for lag in lags]
    return p_value_list


def is_stationary(x: List[int], sig_level: float = 0.05) -> bool:
    test_result = adfuller(x)
    p_val = test_result[1]
    return p_val < sig_level
