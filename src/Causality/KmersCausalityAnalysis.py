from TS.TimeSeriesBuilder import TimeSeriesBuilder
from User.UserType import UserType
from Causality.CausalityAnalysisTool import *

import matplotlib.pyplot as plt
from typing import List


class KmersCausalityAnalysis:
    # Attributes
    ts_builder: TimeSeriesBuilder
    lags: List[int]

    def __init__(self, ts_builder: TimeSeriesBuilder, lags: List[int]):
        self.ts_builder = ts_builder
        self.lags = lags

    def set_lags(self, lags: List[int]) -> None:
        self.lags = lags

    def _plot_lag_to_cause(self, user_type1: UserType, mapping1: str,
                           user_type2: UserType, mapping2: str,
                           cluster_list: List[int]) -> None:
        for cluster_id in cluster_list:
            d_series, s_series = self.ts_builder.create_type_series(
                user_type1, mapping1, user_type2, mapping2, cluster_id)
            p_vals = gc_score_for_lags(d_series, s_series, self.lags)
            plt.plot(self.lags, p_vals, label=cluster_id)
        plt.axhline(y=0.05, color="r", linestyle="--")
        plt.xticks(self.lags)
        plt.xlabel("lags")
        plt.ylabel("p-value")
        plt.legend()
        plt.title(user_type1.value + " " + mapping1 + " to "
                  + user_type2.value + " " + mapping2)
        plt.show()

    def plot_cause_forward(self, cluster_list: List[int]) -> None:
        self._plot_lag_to_cause(UserType.CONSUMER, "demand",
                                UserType.CORE_NODE, "supply", cluster_list)
        self._plot_lag_to_cause(UserType.CORE_NODE, "demand",
                                UserType.PRODUCER, "supply", cluster_list)
        self._plot_lag_to_cause(UserType.CONSUMER, "demand",
                                UserType.PRODUCER, "supply", cluster_list)
        self._plot_lag_to_cause(UserType.CONSUMER, "demand",
                                UserType.CORE_NODE, "demand", cluster_list)

    def plot_cause_backward(self, cluster_list: List[int]) -> None:
        self._plot_lag_to_cause(UserType.CORE_NODE, "supply",
                                UserType.CONSUMER, "demand", cluster_list)
        self._plot_lag_to_cause(UserType.PRODUCER, "supply",
                                UserType.CORE_NODE, "demand", cluster_list)
        self._plot_lag_to_cause(UserType.PRODUCER, "supply",
                                UserType.CONSUMER, "demand", cluster_list)
        self._plot_lag_to_cause(UserType.CORE_NODE, "demand",
                                UserType.CONSUMER, "demand", cluster_list)