from Aggregation.ContentDemandSupply import ContentDemandSupply
from Visualization.MappingPlotter import MappingPlotter
from User.UserType import UserType

from typing import Dict
import matplotlib.pyplot as plt


def _merge_dict(dct1: Dict[int, int], dct2: Dict[int, int]) -> Dict[int, int]:
    """Add value in dct1 and dct2.
    """
    merged_dict = {}

    for key in dct1.keys():
        if key in dct2:
            merged_dict[key] = dct1[key] + dct2[key]
        else:
            merged_dict[key] = dct1[key]

    for key in dct2.keys():
        if key not in dct1:
            merged_dict[key] = dct2[key]

    return merged_dict


class CreatorPlotter(MappingPlotter):
    repr_to_id: Dict[int, int]

    def __init__(self, ds: ContentDemandSupply):
        super().__init__(ds)
        self.repr_to_id = {index: content.get_representation()
                           for index, content in enumerate(ds.content_space)}

    def create_demand_curves(self, is_core_node: bool) -> Dict[int, int]:
        """Create demand bar plot for each ContentType, where the users are
                determined by <is_core_node>.
                """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.CONSUMER
        demand = self.ds.demand_in_community[user_type]

        # convert to numbers
        demand_dict = {key: len(val) for key, val in demand.items()}

        # substitute
        demand = self._sub_id_to_num(demand_dict)
        return demand

    def create_supply_curves(self, is_core_node: bool) -> Dict[int, int]:
        """Create supply bar plot for each ContentType, where the users are
                determined by <is_core_node>.
                """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.PRODUCER
        supply = self.ds.supply[user_type]

        # convert to numbers
        supply_dict = {key: len(val) for key, val in supply.items()}

        # substitute
        supply = self._sub_id_to_num(supply_dict)
        return supply

    def _sub_id_to_num(self, dct: Dict[int, int]) -> Dict[int, int]:
        new_dict = {}
        for key, value in dct.items():
            new_dict[self._find_key_from_value(key)] = value
        return new_dict

    def _find_key_from_value(self, target_key: int) -> int:
        for key, value in self.repr_to_id.items():
            if target_key == value:
                return key

    def create_mapping_curves(self, save: bool) -> None:
        # Core Nodes
        plt.figure()
        core_node_demand = self.create_demand_curves(True)
        core_node_supply = self.create_supply_curves(True)
        plt.bar(core_node_demand.keys(), core_node_demand.values(),
                label="demand", alpha=0.5)
        plt.bar(core_node_supply.keys(), core_node_supply.values(),
                label="supply", alpha=0.5)
        plt.legend()
        plt.title("Supply and Demand for Core Node")
        if save:
            plt.savefig(
                f'../results/creator_' + 'supply_and_demand_for_core_node')
        else:
            plt.show()

        # Ordinary Users
        plt.figure()
        consumer_demand = self.create_demand_curves(False)
        producer_supply = self.create_supply_curves(False)
        plt.bar(consumer_demand.keys(), consumer_demand.values(),
                label="demand", alpha=0.5)
        plt.bar(producer_supply.keys(), producer_supply.values(),
                label="supply", alpha=0.5)
        plt.legend()
        plt.title("Supply and Demand for Ordinary User")
        if save:
            plt.savefig(
                f'../results/creator_' + 'supply_and_demand_for_ordinary_user')
        else:
            plt.show()

        # Aggregate
        plt.figure()
        agg_demand = _merge_dict(core_node_demand, consumer_demand)
        agg_supply = _merge_dict(core_node_supply, producer_supply)
        plt.bar(agg_demand.keys(), agg_demand.values(), label="demand", alpha=0.5)
        plt.bar(agg_supply.keys(), agg_supply.values(), label="supply", alpha=0.5)
        plt.legend()
        plt.title("Aggregate Supply and Demand")
        if save:
            plt.savefig(
                f'../results/creator_agg_supply_and_demand')
        else:
            plt.show()

    def create_demand_time_series(self, is_core_node: bool, save: bool) -> None:
        pass

    def create_supply_time_series(self, is_core_node: bool, save: bool) -> None:
        pass
