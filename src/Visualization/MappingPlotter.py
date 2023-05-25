from User.UserType import UserType
from ContentMarket.ContentMappingManager import ContentMappingManager

import matplotlib.pyplot as plt


def create_demand_curves(is_core_node: bool,
                         mapping_manager: ContentMappingManager) -> None:
    # TODO: docstring for all methods
    if is_core_node:
        demand = mapping_manager.get_agg_demand(UserType.CORE_NODE)
    else:
        demand = mapping_manager.get_agg_demand(UserType.CONSUMER)
    plt.bar(demand.keys(), demand.values(), width=0.4)


def create_supply_curves(is_core_node: bool,
                         mapping_manager: ContentMappingManager) -> None:
    if is_core_node:
        supply = mapping_manager.get_agg_supply(UserType.CORE_NODE)
    else:
        supply = mapping_manager.get_agg_supply(UserType.PRODUCER)
    plt.bar(supply.keys(), supply.values(), width=0.4)


def create_mapping_curves(mapping_manager: ContentMappingManager) -> None:
    plt.figure()
    create_demand_curves(True, mapping_manager)
    create_supply_curves(True, mapping_manager)
    plt.title("Supply and Demand for Core Node")
    plt.show()

    plt.figure()
    create_demand_curves(False, mapping_manager)
    create_supply_curves(False, mapping_manager)
    plt.title("Supply and Demand Curve for Ordinary User")
    plt.show()


def create_demand_time_series(user_type: UserType,
                              mapping_manager: ContentMappingManager) -> None:
    # retrieve value
    time_stamps, demand = mapping_manager.get_type_demand_series(user_type)

    # plot
    plt.figure()
    for type_repr, time_series in demand:
        plt.plot(time_stamps, time_series, label=type_repr)
    plt.title("demand time series")
    plt.legend()
    plt.show()


def create_supply_time_series(user_type: UserType,
                              mapping_manager: ContentMappingManager) -> None:
    # retrieve value
    time_stamps, supply = mapping_manager.get_type_supply_series(user_type)

    # plot
    plt.figure()
    for type_repr, time_series in supply:
        plt.plot(time_stamps, time_series, label=type_repr)
    plt.title("supply time series")
    plt.legend()
    plt.show()
