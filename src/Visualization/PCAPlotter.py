from User.UserType import UserType
from ContentMarket.ContentMappingManager import ContentMappingManager
from Visualization.MappingPlotter import MappingPlotter

from typing import List
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


class PCAPlotter(MappingPlotter):
    # Attributes
    num_dimensions: int
    X: List[List[float]]
    producer_supply_idxs: List[int]
    consumer_demand_idxs: List[int]
    core_node_supply_idxs: List[int]
    core_node_demand_idxs: List[int]

    def __init__(self, num_dimensions: int, full_mapping_manager: ContentMappingManager, 
                 plotting_mapping_manager: ContentMappingManager) -> None:
        super().__init__()
        self.num_dimensions = num_dimensions
        self.X = self._calculate_X(full_mapping_manager)
        self.producer_supply_idxs, self.consumer_demand_idxs, \
            self.core_node_supply_idxs, self.core_node_demand_idxs \
                = self._calculate_idx_lists(full_mapping_manager, plotting_mapping_manager)


    def create_demand_curves(self, is_core_node: bool,
                             mapping_manager: ContentMappingManager,
                             save: bool) -> None:
        """Create demand bar plot for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.CONSUMER
        # Plot
        pca = PCA(n_components=self.num_dimensions)
        pca.fit(np.transpose(np.asarray(self.X)))
        # reset the figure if save == True
        if save:
            plt.figure()
        if self.num_dimensions == 1:
            if user_type == UserType.CORE_NODE:
                ax = sns.histplot(pca.components_[0][self.core_node_demand_idxs], kde=True, color="green", label=user_type.value + " demand")
                ax.containers[0].remove()  # remove the bars
            else:
                ax = sns.histplot(pca.components_[0][self.consumer_demand_idxs], kde=True, color="blue", label=user_type.value + " demand")
                ax.containers[0].remove()  # remove the bars
        elif self.num_dimensions == 2:
            if user_type == UserType.CORE_NODE:
                plt.scatter(pca.components_[0][self.core_node_demand_idxs], pca.components_[1][self.core_node_demand_idxs], 
                            color="green", marker="x", alpha=0.05, label=user_type.value + " demand")
                plt.ylim((-0.01173576866741382, 0.013412482077072655))
                plt.xlim((-0.0015774123311422977, 0.006602585335744285))
            else:
                plt.scatter(pca.components_[0][self.consumer_demand_idxs], pca.components_[1][self.consumer_demand_idxs], 
                            color="blue", marker="o", alpha=0.05, label=user_type.value + " demand")
                plt.ylim((-0.01173576866741382, 0.013412482077072655))
                plt.xlim((-0.0015774123311422977, 0.006602585335744285))
        if save:
            plt.savefig(f'../results/pca' + str(self.num_dimensions) + 'd_' + 'demand_for_' + user_type.value)
            plt.clf()

    def create_supply_curves(self, is_core_node: bool,
                             mapping_manager: ContentMappingManager,
                             save: bool) -> None:
        """Create supply bar plot for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # Retrieve Data
        user_type = UserType.CORE_NODE if is_core_node else UserType.PRODUCER
        # Plot
        pca = PCA(n_components=self.num_dimensions)
        pca.fit(np.transpose(np.asarray(self.X)))
        if save:
            plt.figure()
        if self.num_dimensions == 1:
            if user_type == UserType.CORE_NODE:
                ax = sns.histplot(pca.components_[0][self.core_node_supply_idxs], kde=True, color="yellow", label=user_type.value + " supply")
                ax.containers[0].remove()  # remove the bars
            else:
                ax = sns.histplot(pca.components_[0][self.producer_supply_idxs], kde=True, color="red", label=user_type.value + " supply")
                ax.containers[0].remove()  # remove the bars
        elif self.num_dimensions == 2:
            if user_type == UserType.CORE_NODE:
                plt.scatter(pca.components_[0][self.core_node_supply_idxs], pca.components_[1][self.core_node_supply_idxs], 
                            color="yellow", marker="x", alpha=0.05, label=user_type.value + " supply")
                plt.ylim((-0.01173576866741382, 0.013412482077072655))
                plt.xlim((-0.0015774123311422977, 0.006602585335744285))
            else:
                plt.scatter(pca.components_[0][self.producer_supply_idxs], pca.components_[1][self.producer_supply_idxs], 
                            color="red", marker="o", alpha=0.05, label=user_type.value + " supply")
                plt.ylim((-0.01173576866741382, 0.013412482077072655))
                plt.xlim((-0.0015774123311422977, 0.006602585335744285))
        if save:
            plt.savefig(f'../results/pca' + str(self.num_dimensions) + 'd_' + 'supply_for_' + user_type.value)
            plt.clf()

    def create_mapping_curves(self, mapping_manager: ContentMappingManager,
                              save: bool) -> None:
        """Create both supply and demand bar plots for core node and ordinary user.
        """
        plt.figure()
        self.create_supply_curves(is_core_node=False, mapping_manager=mapping_manager, save=False)
        self.create_demand_curves(is_core_node=False, mapping_manager=mapping_manager, save=False)
        self.create_supply_curves(is_core_node=True, mapping_manager=mapping_manager, save=False)
        self.create_demand_curves(is_core_node=True, mapping_manager=mapping_manager, save=False)
        print(plt.gca().get_ylim())
        print(plt.gca().get_xlim())
        plt.legend(labels=["producer supply", "consumer demand", "core node supply", "core node demand"])
        plt.title("Supply and Demand")
        if save:
            plt.savefig(f'../results/pca' + str(self.num_dimensions) + 'd_' + 'supply_and_demand')
            plt.clf()
    
    # def compute_correlation_matrix(self):
    #     assert self.num_dimensions == 1  # this function only works for the 1D case
    #     pca = PCA(n_components=self.num_dimensions)
    #     pca.fit(np.transpose(np.asarray(self.X)))
    #     data = []
    #     print(pca.components_[0][self.core_node_demand_idxs])
    #     g = sns.histplot(pca.components_[0][self.core_node_demand_idxs], kde=True, color="green", label="core_node_" + " demand")
    #     heights = []
    #     for rectangle in g.patches:
    #         heights.append(rectangle.get_height())
    #     print(len(heights))


    def create_demand_time_series(self, is_core_node: bool,
                                 mapping_manager: ContentMappingManager,
                                 save: bool) -> None:
        """Create demand time series for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # TODO: Implement
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
                                  mapping_manager: ContentMappingManager,
                                  save: bool) -> None:
        """Create demand time series for each ContentType, where the users are
        determined by <is_core_node>.
        """
        # TODO: Implement
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

    def _calculate_X(self, full_mapping_manager: ContentMappingManager):
        """Calculate X, which is the original embedding before PCA is performed."""
        full_producer_supply = full_mapping_manager.get_agg_supply(UserType.PRODUCER)
        full_consumer_demand = full_mapping_manager.get_agg_demand(UserType.CONSUMER)
        full_core_node_supply = full_mapping_manager.get_agg_supply(UserType.CORE_NODE)
        full_core_node_demand = full_mapping_manager.get_agg_demand(UserType.CORE_NODE)
        
        X = []
        for embedding in full_producer_supply:
            for _ in range(full_producer_supply[embedding]):
                X.append(embedding)
        for embedding in full_consumer_demand:
            for _ in range(full_consumer_demand[embedding]):
                X.append(embedding)
        for embedding in full_core_node_supply:
            for _ in range(full_core_node_supply[embedding]):
                X.append(embedding)
        for embedding in full_core_node_demand:
            for _ in range(full_core_node_demand[embedding]):
                X.append(embedding)
        
        # print(len(X))
        # print(sum(full_producer_supply[e] for e in full_producer_supply) + sum(full_consumer_demand[e] for e in full_consumer_demand) + sum(full_core_node_supply[e] for e in full_core_node_supply) + sum(full_core_node_demand[e] for e in full_core_node_demand))
        return X
    
    def _calculate_idx_lists(self, full_mapping_manager: ContentMappingManager,
                             plotting_mapping_manager: ContentMappingManager):
        
        full_producer_supply = full_mapping_manager.get_agg_supply(UserType.PRODUCER)
        full_consumer_demand = full_mapping_manager.get_agg_demand(UserType.CONSUMER)
        full_core_node_supply = full_mapping_manager.get_agg_supply(UserType.CORE_NODE)
        full_core_node_demand = full_mapping_manager.get_agg_demand(UserType.CORE_NODE)
        plotting_producer_supply = plotting_mapping_manager.get_agg_supply(UserType.PRODUCER)
        plotting_consumer_demand = plotting_mapping_manager.get_agg_demand(UserType.CONSUMER)
        plotting_core_node_supply = plotting_mapping_manager.get_agg_supply(UserType.CORE_NODE)
        plotting_core_node_demand = plotting_mapping_manager.get_agg_demand(UserType.CORE_NODE)

        producer_supply_idxs, consumer_demand_idxs, core_node_supply_idxs, core_node_demand_idxs \
            = [], [], [], []
        
        i = 0

        for embedding in full_producer_supply:
            if embedding in plotting_producer_supply:
                for _ in range(plotting_producer_supply[embedding]):
                    producer_supply_idxs.append(i)
                    i += 1
                for _ in range(full_producer_supply[embedding] - plotting_producer_supply[embedding]):
                    i += 1
            else:
                for _ in range(full_producer_supply[embedding]):
                    i += 1
        for embedding in full_consumer_demand:
            if embedding in plotting_consumer_demand:
                for _ in range(plotting_consumer_demand[embedding]):
                    consumer_demand_idxs.append(i)
                    i += 1
                for _ in range(full_consumer_demand[embedding] - plotting_consumer_demand[embedding]):
                    i += 1
            else:
                for _ in range(full_consumer_demand[embedding]):
                    i += 1
        for embedding in full_core_node_supply:
            if embedding in plotting_core_node_supply:
                for _ in range(plotting_core_node_supply[embedding]):
                    core_node_supply_idxs.append(i)
                    i += 1
                for _ in range(full_core_node_supply[embedding] - plotting_core_node_supply[embedding]):
                    i += 1
            else:
                for _ in range(full_core_node_supply[embedding]):
                    i += 1
        for embedding in full_core_node_demand:
            if embedding in plotting_core_node_demand:
                for _ in range(plotting_core_node_demand[embedding]):
                    core_node_demand_idxs.append(i)
                    i += 1
                for _ in range(full_core_node_demand[embedding] - plotting_core_node_demand[embedding]):
                    i += 1
            else:
                for _ in range(full_core_node_demand[embedding]):
                    i += 1

        # print("i: " + str(i))
        # print(len(core_node_demand_idxs))
        # print(len(core_node_supply_idxs))
        # print(len(consumer_demand_idxs))
        # print(len(producer_supply_idxs))
        
        return producer_supply_idxs, consumer_demand_idxs, \
            core_node_supply_idxs, core_node_demand_idxs

