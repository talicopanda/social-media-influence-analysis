from typing import List
import warnings
import pandas as pd

warnings.simplefilter(action='ignore', category=FutureWarning)
from statsmodels.tsa.stattools import grangercausalitytests


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
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": dep_series,
        "y": indep_series
    }), maxlag=lags, verbose=verbose)
    p_value_list = [granger_test[lag][0][test][1] for lag in lags]
    return p_value_list
