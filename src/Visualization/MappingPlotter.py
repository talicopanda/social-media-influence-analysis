from abc import ABC, abstractmethod

from Aggregation.ContentDemandSupply import ContentDemandSupply

from typing import Dict


class MappingPlotter(ABC):
    """Abstract class for visualizing the Content Market.
    """
    ds: ContentDemandSupply

    def __init__(self, ds: ContentDemandSupply):
        self.ds = ds

    @abstractmethod
    def create_demand_curves(self, is_core_node: bool) -> Dict:
        pass

    @abstractmethod
    def create_supply_curves(self, is_core_node: bool) -> Dict:
        pass

    @abstractmethod
    def create_mapping_curves(self, save: bool) -> Dict:
        pass

    @abstractmethod
    def create_demand_time_series(self, is_core_node: bool, save: bool) -> None:
        pass

    @abstractmethod
    def create_supply_time_series(self, is_core_node: bool, save: bool) -> None:
        pass
