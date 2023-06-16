from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType
from Causality.CausalityAnalysisTool import *

from statsmodels.tools.sm_exceptions import InfeasibleTestError
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Any


class CreatorCausalityAnalysis:
    # Attributes
    ds: ContentDemandSupply

    def __init__(self, ds: ContentDemandSupply):
        self.ds = ds

    def consumer_to_core_node_all(self, lags: List[int]) -> List[float]:
        """Return a list of p values for Granger causality test with <lags>
        for all consumers' demand and all core nodes' supply.
        """
        # create consumer demand time series
        consumer_series = list(self.ds.get_type_demand_series(UserType.CONSUMER)[1].values())
        consumer_series = np.array(consumer_series).sum(axis=0)

        # create core node supply time series
        core_node_series = list(self.ds.get_type_supply_series(UserType.CORE_NODE)[1].values())
        core_node_series = np.array(core_node_series).sum(axis=0)

        # get granger score
        return gc_score_for_lags(consumer_series, core_node_series, lags)

    def core_node_to_producer_all(self, lags: List[int]) -> List[float]:
        """Return a list of p values for Granger causality test with <lags>
        for all core nodes' demand and all producers' supply.
        """
        # create core node demand time series
        core_node_series = list(self.ds.get_type_demand_series(UserType.CORE_NODE)[1].values())
        core_node_series = np.array(core_node_series).sum(axis=0)

        # create producer supply time series
        # create core node supply time series
        producer_series = list(self.ds.get_type_supply_series(UserType.PRODUCER)[1].values())
        producer_series = np.array(producer_series).sum(axis=0)

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
        core_node_list = [user.user_id for user in self.ds.user_manager.core_nodes]
        for content_type_repr in self.ds.get_content_type_repr():
            if int(content_type_repr) in core_node_list:
                continue
            consumer_series = self.ds.get_type_demand_series(UserType.CONSUMER)[content_type_repr]
            core_node_series = self.ds.get_type_supply_series(UserType.CORE_NODE)[content_type_repr]
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
        core_node_list = [user.user_id for user in self.ds.user_manager.core_nodes]
        for content_type_repr in self.ds.get_content_type_repr():
            if int(content_type_repr) in core_node_list:
                continue
            core_node_series = self.ds.get_type_demand_series(UserType.CORE_NODE)[content_type_repr]
            producer_series = self.ds.get_type_supply_series(UserType.PRODUCER)[content_type_repr]
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
        key_dict, c2c_score_dict = self._create_num_type_mapping(c2c_score_dict)
        c2p_score_dict = self._convert_num_type_mapping(c2p_score_dict, key_dict)

        # cleaning
        c2c_storage = {}
        for key, value in c2c_score_dict.items():
            if value != 1:
                c2c_storage[key] = value
        c2c_score_dict = c2c_storage

        c2p_storage = {}
        for key, value in c2p_score_dict.items():
            if value != 1:
                c2p_storage[key] = value
        c2p_score_dict = c2p_storage

        # plot
        plt.figure()
        x_tick = list(c2c_score_dict.keys())
        plt.bar(c2c_score_dict.keys(), c2c_score_dict.values(),
                label="consumer to core node", alpha=0.5)
        plt.axhline(y=sig_level, color="red", linestyle="--")
        plt.xticks(x_tick)
        plt.legend()
        plt.title("Granger Score for Different ContentType")
        plt.show()

        plt.figure()
        x_tick = list(c2p_score_dict.keys())
        plt.bar(c2p_score_dict.keys(), c2p_score_dict.values(),
                label="core node to producer", alpha=0.5)
        plt.axhline(y=sig_level, color="red", linestyle="--")
        plt.xticks(x_tick)
        plt.legend()
        plt.title("Granger Score for Different ContentType")
        plt.show()

    def _create_num_type_mapping(self, raw_dict: Dict) -> (Dict[str, Any], Dict):
        """Return a mapping of string '1', '2', '3', ... to keys in <raw_dict>,
        and '1', '2', '3', ... to values in <raw_dict>. The original key-value
        pair correspond to the same key in the return dictionaries.
        """
        acc = "0"
        key_dict = {}
        data_dict = {}
        for key, value in raw_dict.items():
            key_dict[acc] = key
            data_dict[acc] = value
            acc = str(int(acc) + 1)
        return key_dict, data_dict

    def _convert_num_type_mapping(self, raw_dict: Dict, key_dict: Dict[str, Any]) -> Dict:
        """Return a dictionary with <raw_dict>'s keys changed to corresponding
        keys in <key_dict>.
        """
        data_dict = {}
        for key, value in raw_dict.items():
            data_dict[self.get_key_from_value(key_dict, key)] = value
        return data_dict

    def get_key_from_value(self, raw_dict: Dict, value: Any) -> Any:
        """Return the key that maps to <value> in <raw_dict>.
        """
        for k, v in raw_dict.items():
            if v == value:
                return k
