from typing import List
from statsmodels.tsa.stattools import grangercausalitytests
import pandas as pd


def granger_cause_score(series1: List[int], series2: List[int], lag: int) -> float:
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": series1,
        "y": series2
    }), maxlag=[lag])
    return granger_test[2][0]["ssr_ftest"][1]


def granger_cause_score(series1: List[int], series2: List[int], lags: List[int]) -> (int, float):
    granger_test = grangercausalitytests(pd.DataFrame({
        "x": series1,
        "y": series2
    }), maxlag=lags)
    p_value_list = [granger_test[lag][0]["ssr_ftest"][1] for lag in lags]
    min_idx = p_value_list.index(min(p_value_list))
    return p_value_list[min_idx], lags[min_idx]
