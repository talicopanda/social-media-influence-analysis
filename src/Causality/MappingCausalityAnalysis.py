from ContentMarket.ContentMappingManager import ContentMappingManager
from User.UserType import UserType
from Causality.CausalityAnalysis import *
from statsmodels.tools.sm_exceptions import InfeasibleTestError

import numpy as np
from typing import List, Dict, Any


class MappingCausalityAnalysis:
    # Attributes
    mapping_manager: ContentMappingManager

    def __init__(self, mapping_manager: ContentMappingManager):
        self.mapping_manager = mapping_manager

    def consumer_to_core_node_all(self, lags: List[int]) -> List[float]:
        # create consumer demand time series
        consumer_series = list(self.mapping_manager.get_type_demand_series(UserType.CONSUMER)[1].values())
        consumer_series = np.array(consumer_series).sum(axis=0)

        # create core node supply time series
        core_node_series = list(self.mapping_manager.get_type_supply_series(UserType.CORE_NODE)[1].values())
        core_node_series = np.array(core_node_series).sum(axis=0)

        # get granger score
        return gc_score_for_lags(consumer_series, core_node_series, lags)

    def core_node_to_producer_all(self, lags: List[int]) -> List[float]:
        # create core node demand time series
        core_node_series = list(self.mapping_manager.get_type_demand_series(UserType.CORE_NODE)[1].values())
        core_node_series = np.array(core_node_series).sum(axis=0)

        # create producer supply time series
        # create core node supply time series
        producer_series = list(self.mapping_manager.get_type_supply_series(UserType.PRODUCER)[1].values())
        producer_series = np.array(producer_series).sum(axis=0)

        # get granger score
        return gc_score_for_lags(core_node_series, producer_series, lags)

    def consumer_to_core_node_type(self, lags: List[int]) -> Dict[Any, float]:
        p_dict = {}
        for content_type_repr in self.mapping_manager.get_content_type_repr():
            consumer_series = self.mapping_manager.get_type_demand_series(UserType.CONSUMER)[1][content_type_repr]
            core_node_series = self.mapping_manager.get_type_supply_series(UserType.CORE_NODE)[1][content_type_repr]
            try:
                p_dict[content_type_repr] = min(gc_score_for_lags(consumer_series,
                                                                  core_node_series,
                                                                  lags))
            except InfeasibleTestError:
                print(f"ContentType {content_type_repr} has constant series")
                p_dict[content_type_repr] = 1
        return p_dict

    def core_node_to_producer_type(self, lags: List[int]) -> Dict[Any, float]:
        p_dict = {}
        for content_type_repr in self.mapping_manager.get_content_type_repr():
            core_node_series = self.mapping_manager.get_type_demand_series(UserType.CORE_NODE)[1][content_type_repr]
            producer_series = self.mapping_manager.get_type_supply_series(UserType.PRODUCER)[1][content_type_repr]
            p_dict[content_type_repr] = min(gc_score_for_lags(core_node_series,
                                                              producer_series,
                                                              lags))
        return p_dict
