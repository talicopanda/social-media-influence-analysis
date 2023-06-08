from abc import ABC, abstractmethod

from Aggregation.ContentDemandSupply import ContentDemandSupply


class MappingPlotter(ABC):
    """Abstract class for visualizing the Content Market"""

    @abstractmethod
    def create_demand_curves(self, is_core_node: bool,
                             mapping_manager: ContentDemandSupply,
                             save: bool) -> None:
        pass



    @abstractmethod
    def create_supply_curves(self, is_core_node: bool,
                             mapping_manager: ContentDemandSupply,
                             save: bool) -> None:
        pass


    @abstractmethod
    def create_mapping_curves(self, mapping_manager: ContentDemandSupply,
                              save: bool) -> None:
        pass


    @abstractmethod
    def create_demand_time_series(self, is_core_node: bool,
                                  mapping_manager: ContentDemandSupply,
                                  save: bool) -> None:
        pass


    @abstractmethod
    def create_supply_time_series(self, is_core_node: bool,
                                  mapping_manager: ContentDemandSupply,
                                  save: bool) -> None:
        pass
