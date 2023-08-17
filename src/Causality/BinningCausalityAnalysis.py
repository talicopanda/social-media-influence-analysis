from TS.TimeSeriesBuilderBase import TimeSeriesBuilderBase
from User.UserType import UserType
from Causality.CausalityAnalysisTool import *

import matplotlib.pyplot as plt
from typing import List


class BinningCausalityAnalysis:
    # Attributes
    ts_builder: TimeSeriesBuilderBase
    lags: List[int]

    def __init__(self, ts_builder: TimeSeriesBuilderBase, lags: List[int]):
        self.ts_builder = ts_builder
        self.lags = lags

    def _plot_lag_to_cause(self, user_type1: UserType, mapping1: str,
                           user_type2: UserType, mapping2: str,
                           cluster_list: List[int], save: bool) -> None:
        plt.figure()
        for cluster_id in cluster_list:
            d_series = self.ts_builder.create_time_series(user_type1,
                                                          cluster_id, mapping1)
            s_series = self.ts_builder.create_time_series(user_type2,
                                                          cluster_id, mapping2)

            # process series
            # d_series = np.diff(d_series)
            # s_series = np.diff(s_series)

            p_vals = gc_score_for_lags(d_series, s_series, self.lags)
            plt.plot(self.lags, p_vals, label=cluster_id)
        plt.axhline(y=0.05, color="r", linestyle="--")
        plt.xticks(self.lags)
        plt.xlabel("lags")
        plt.ylabel("p-value")
        plt.legend()
        title = "binning filtered " + user_type1.value + " " + mapping1 + " to " \
                + user_type2.value + " " + mapping2
        plt.title(title)
        if save:
            plt.savefig('../results/' + title)
        else:
            plt.show()

    def plot_cause_forward(self, cluster_list: List[int], save: bool) -> None:
        self._plot_lag_to_cause(UserType.CONSUMER, "demand_in_community",
                                UserType.CORE_NODE, "supply",
                                cluster_list, save)
        self._plot_lag_to_cause(UserType.CORE_NODE, "demand_in_community",
                                UserType.PRODUCER, "supply",
                                cluster_list, save)
        self._plot_lag_to_cause(UserType.CONSUMER, "demand_in_community",
                                UserType.PRODUCER, "supply",
                                cluster_list, save)
        self._plot_lag_to_cause(UserType.CONSUMER, "demand_in_community",
                                UserType.CORE_NODE, "demand_in_community",
                                cluster_list, save)

    def plot_cause_backward(self, cluster_list: List[int], save: bool) -> None:
        self._plot_lag_to_cause(UserType.CORE_NODE, "supply",
                                UserType.CONSUMER, "demand_in_community",
                                cluster_list, save)
        self._plot_lag_to_cause(UserType.PRODUCER, "supply",
                                UserType.CORE_NODE, "demand_in_community",
                                cluster_list, save)
        self._plot_lag_to_cause(UserType.PRODUCER, "supply",
                                UserType.CONSUMER, "demand_in_community",
                                cluster_list, save)
        self._plot_lag_to_cause(UserType.CORE_NODE, "demand_in_community",
                                UserType.CONSUMER, "demand_in_community",
                                cluster_list, save)
