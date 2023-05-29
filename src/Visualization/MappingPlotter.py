from abc import ABC, abstractmethod

from User.UserType import UserType
from ContentMarket.ContentMappingManager import ContentMappingManager

import matplotlib.pyplot as plt


class MappingPlotter(ABC):
    """Abstract class for visualizing the Content Market"""

    @abstractmethod
    def create_demand_curves(self, is_core_node: bool, 
                             mapping_manager: ContentMappingManager,
                             save: bool) -> None:
        pass
        


    @abstractmethod
    def create_supply_curves(self, is_core_node: bool,
                             mapping_manager: ContentMappingManager,
                             save: bool) -> None:
        pass


    @abstractmethod
    def create_mapping_curves(self, mapping_manager: ContentMappingManager,
                              save: bool) -> None:
        pass


    @abstractmethod
    def create_demand_time_series(self, is_core_node: bool,
                                  mapping_manager: ContentMappingManager,
                                  save: bool) -> None:
        pass


    @abstractmethod
    def create_supply_time_series(self, is_core_node: bool,
                                  mapping_manager: ContentMappingManager,
                                  save: bool) -> None:
        pass