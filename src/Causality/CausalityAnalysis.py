from typing import List
from statsmodels.tsa.stattools import grangercausalitytests
import pandas as pd


def gc_score_for_lag(indep_series: List[int],
                     dep_series: List[int], lag: int) -> float:
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": indep_series,
        "y": dep_series
    }), maxlag=[lag])
    return granger_test[lag][0]["ssr_ftest"][1]


def gc_score_for_lags(indep_series: List[int],
                      dep_series: List[int], lags: List[int]) -> List[float]:
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": indep_series,
        "y": dep_series
    }), maxlag=lags)
    p_value_list = [granger_test[lag][0]["ssr_ftest"][1] for lag in lags]
    return p_value_list
