from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType
from Causality.CausalityAnalysisTool import *

from statsmodels.tools.sm_exceptions import InfeasibleTestError
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any


class MappingCausalityAnalysis:
    # Attributes
    mapping_manager: ContentDemandSupply

    def __init__(self, mapping_manager: ContentDemandSupply):
        self.mapping_manager = mapping_manager

    def consumer_to_core_node_all(self, lags: List[int]) -> List[float]:
        """Return a list of p values for Granger causality test with <lags>
        for all consumers' demand and all core nodes' supply.
        """
        # create consumer demand time series
        consumer_series = list(self.mapping_manager.get_type_demand_series(UserType.CONSUMER).values())
        consumer_series = np.array(consumer_series).sum(axis=0)
        if not is_stationary(consumer_series):
            print("Consumer demand series is not stationary")

        # create core node supply time series
        core_node_series = list(self.mapping_manager.get_type_supply_series(UserType.CORE_NODE).values())
        core_node_series = np.array(core_node_series).sum(axis=0)
        if not is_stationary(core_node_series):
            print("Core Node supply series is not stationary")

        # get granger score
        return gc_score_for_lags(consumer_series, core_node_series, lags)

    def core_node_to_producer_all(self, lags: List[int]) -> List[float]:
        """Return a list of p values for Granger causality test with <lags>
        for all core nodes' demand and all producers' supply.
        """
        # create core node demand time series
        core_node_series = list(self.mapping_manager.get_type_demand_series(UserType.CORE_NODE).values())
        core_node_series = np.array(core_node_series).sum(axis=0)
        if not is_stationary(core_node_series):
            print("Core Node demand series is not stationary")

        # create producer supply time series
        # create core node supply time series
        producer_series = list(self.mapping_manager.get_type_supply_series(UserType.PRODUCER).values())
        producer_series = np.array(producer_series).sum(axis=0)
        if not is_stationary(producer_series):
            print("Producer supply series is not stationary")

        # get granger score
        return gc_score_for_lags(core_node_series, producer_series, lags)

    def mapping_cause_all(self, lags: List[int], sig_level: float = 0.05) -> None:
        """Plot the p values for different <lags> by Granger Causality test
        for the relationship between all consumers, core nodes, and producers.
        """
        # calculate causality score
        c2c_scores = self.consumer_to_core_node_all(lags)
        c2p_scores = self.core_node_to_producer_all(lags)

        # plot
        plt.figure()
        plt.plot(lags, c2c_scores, "^--", label="consumer to core node")
        plt.plot(lags, c2p_scores, "o-.", label="core node to producer")
        plt.axhline(y=sig_level, color="red", linestyle="--")
        plt.legend()
        plt.xticks(lags)
        plt.title("Granger Score for All Users")
        plt.show()

    def consumer_to_core_node_type(self, lags: List[int]) -> Dict[Any, float]:
        """Return a list of p values for Granger causality test with <lags>
        within different ContentTypes for consumers and core nodes.
        """
        p_dict = {}
        for content_type_repr in self.mapping_manager.get_content_type_repr():
            consumer_series = self.mapping_manager.get_type_demand_series(UserType.CONSUMER)[content_type_repr]
            core_node_series = self.mapping_manager.get_type_supply_series(UserType.CORE_NODE)[content_type_repr]
            try:
                p_dict[content_type_repr] = min(gc_score_for_lags(consumer_series,
                                                                  core_node_series,
                                                                  lags))
            except InfeasibleTestError:
                print(f"ContentType {content_type_repr} has constant series")
                p_dict[content_type_repr] = 1
        return p_dict

    def core_node_to_producer_type(self, lags: List[int]) -> Dict[Any, float]:
        """Return a list of p values for Granger causality test with <lags>
        within different ContentTypes for core nodes and producers.
        """
        p_dict = {}
        for content_type_repr in self.mapping_manager.get_content_type_repr():
            core_node_series = self.mapping_manager.get_type_demand_series(UserType.CORE_NODE)[content_type_repr]
            producer_series = self.mapping_manager.get_type_supply_series(UserType.PRODUCER)[content_type_repr]
            try:
                p_dict[content_type_repr] = min(gc_score_for_lags(core_node_series,
                                                                  producer_series,
                                                                  lags))
            except InfeasibleTestError:
                print(f"ContentType {content_type_repr} has constant series")
                p_dict[content_type_repr] = 1
        return p_dict

    def mapping_cause_type(self, lags: List[int], sig_level: float = 0.05) -> None:
        """Plot the p values for different <lags> by Granger Causality test
        for each ContentType for the relationship between consumers, core nodes,
        and producers.
        """
        # calculate causality score
        c2c_score_dict = self.consumer_to_core_node_type(lags)
        c2p_score_dict = self.core_node_to_producer_type(lags)

        # plot
        plt.figure()
        x_tick = list(c2c_score_dict.keys())
        plt.bar(c2c_score_dict.keys(), c2c_score_dict.values(),
                label="consumer to core node", alpha=0.5)
        plt.bar(c2p_score_dict.keys(), c2p_score_dict.values(),
                label="core node to producer", alpha=0.5)
        plt.axhline(y=sig_level, color="red", linestyle="--")
        plt.xticks(x_tick)
        plt.legend()
        plt.title("Granger Score for Different ContentType")
        plt.show()
