from User.UserType import UserType
from ContentMarket.ContentMappingManager import ContentMappingManager

import matplotlib.pyplot as plt


def create_demand_curves(user_type: UserType,
                         mapping_manager: ContentMappingManager) -> None:
    # TODO: docstring for all methods
    # retrieve value
    demand = mapping_manager.get_agg_demand(user_type)

    # plot
    plt.figure()
    plt.bar(demand.keys(), demand.values())
    plt.title("demand by ContentType")
    plt.show()


def create_supply_curves(user_type: UserType,
                         mapping_manager: ContentMappingManager) -> None:
    # retrieve value
    supply = mapping_manager.get_agg_supply(user_type)

    # plot
    plt.figure()
    plt.bar(supply.keys(), supply.values())
    plt.title("supply by ContentType")
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
