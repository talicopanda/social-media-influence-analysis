from User.UserType import UserType
from Aggregation.ContentDemandSupply import ContentDemandSupply
from Visualization.MappingPlotter import MappingPlotter

import matplotlib.pyplot as plt


class KmersPlotter(MappingPlotter):
    def create_demand_curves(self, is_core_node: bool,
                             mapping_manager: ContentDemandSupply,
                             save: bool) -> None:
        """Create demand bar plot for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.CONSUMER
        demand = mapping_manager.get_agg_demand(user_type)
        # Plot
        plt.bar(demand.keys(), demand.values(), width=0.4)
        if save:
            plt.savefig(f'../results/kmers_' + 'demand_for_' + user_type.value)


    def create_supply_curves(self, is_core_node: bool,
                             mapping_manager: ContentDemandSupply,
                             save: bool) -> None:
        """Create supply bar plot for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.PRODUCER
        supply = mapping_manager.get_agg_supply(user_type)
        # Plot
        plt.bar(supply.keys(), supply.values(), width=0.4)
        if save:
            plt.savefig(f'../results/kmers_' + 'supply_for_' + user_type.value)


    def create_mapping_curves(self, mapping_manager: ContentDemandSupply,
                              save: bool) -> None:
        """Create both supply and demand bar plots for core node and ordinary user.
        """
        # Core Nodes
        plt.figure()
        self.create_demand_curves(True, mapping_manager, False)
        self.create_supply_curves(True, mapping_manager, False)
        plt.title("Supply and Demand for Core Node")
        if save:
            plt.savefig(f'../results/kmers_' + 'supply_and_demand_for_core_node')

        # Ordinary Users
        plt.figure()
        self.create_demand_curves(False, mapping_manager, False)
        self.create_supply_curves(False, mapping_manager, False)
        plt.title("Supply and Demand for Ordinary User")
        if save:
            plt.savefig(f'../results/kmers_' + 'supply_and_demand_for_ordinary_user')


    def create_demand_time_series(self, is_core_node: bool,
                                  mapping_manager: ContentDemandSupply,
                                  save: bool) -> None:
        """Create demand time series for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.CONSUMER
        time_stamps, demand = mapping_manager.get_type_demand_series(user_type)

        # Plot
        plt.figure()
        for type_repr, time_series in demand:
            plt.plot(time_stamps, time_series, label=type_repr)
        plt.title("demand time series")
        plt.legend()
        if save:
            plt.savefig(f'../results/kmers_' + 'demand_time_series')


    def create_supply_time_series(self, is_core_node: bool,
                                  mapping_manager: ContentDemandSupply,
                                  save: bool) -> None:
        """Create demand time series for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.CONSUMER
        time_stamps, supply = mapping_manager.get_type_supply_series(user_type)

        # Plot
        plt.figure()
        for type_repr, time_series in supply:
            plt.plot(time_stamps, time_series, label=type_repr)
        plt.title("supply time series")
        plt.legend()
        if save:
            plt.savefig(f'../results/kmers_' + 'supply_time_series')
