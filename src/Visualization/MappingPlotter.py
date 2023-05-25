from User.UserType import UserType
from ContentMarket.ContentMappingManager import ContentMappingManager

import matplotlib.pyplot as plt


def create_demand_curves(is_core_node: bool,
                         mapping_manager: ContentMappingManager) -> None:
    """Create demand bar plot for each ContentType, where the users are
    determined by <is_core_node>.
    """
    # Retrieve Data
    user_type = UserType.CORE_NODE if is_core_node else UserType.CONSUMER
    demand = mapping_manager.get_agg_demand(user_type)
    # Plot
    plt.bar(demand.keys(), demand.values(), width=0.4)


def create_supply_curves(is_core_node: bool,
                         mapping_manager: ContentMappingManager) -> None:
    """Create supply bar plot for each ContentType, where the users are
    determined by <is_core_node>.
    """
    # Retrieve Data
    user_type = UserType.CORE_NODE if is_core_node else UserType.PRODUCER
    supply = mapping_manager.get_agg_supply(user_type)
    # Plot
    plt.bar(supply.keys(), supply.values(), width=0.4)


def create_mapping_curves(mapping_manager: ContentMappingManager) -> None:
    """Create both supply and demand bar plots for core node and ordinary user.
    """
    # Core Nodes
    plt.figure()
    create_demand_curves(True, mapping_manager)
    create_supply_curves(True, mapping_manager)
    plt.title("Supply and Demand for Core Node")
    plt.show()

    # Ordinary Users
    plt.figure()
    create_demand_curves(False, mapping_manager)
    create_supply_curves(False, mapping_manager)
    plt.title("Supply and Demand Curve for Ordinary User")
    plt.show()


def create_demand_time_series(is_core_node: bool,
                              mapping_manager: ContentMappingManager) -> None:
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
    plt.show()


def create_supply_time_series(is_core_node: bool,
                              mapping_manager: ContentMappingManager) -> None:
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
    plt.show()
