from DAO.ContentMarketFactory import ContentMarketFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Tweet.ContentMarketTweetManager import ContentMarketTweetManager
from User.ContentMarketUserManager import ContentMarketUserManager
from Clustering.ContentMarketClusteringFactory import \
    ContentMarketClusteringFactory
from ContentSpace.ContentSpace import ContentSpace
from Visualization.KmersPlotter import KmersPlotter
from ContentMarket.ContentMappingManager import ContentMappingManager
from Causality.MappingCausalityAnalysis import MappingCausalityAnalysis

import json
import sys
import pickle
import pymongo
from analysis import *
from datetime import timedelta


def build_content_market(content_market_name, config, load=False):
    ##########################################################
    # Pre check
    ##########################################################
    if config['database']['db_type'] != "Mongo":
        raise Exception("Unsupported database type")

    # check if a content market database with the given name already exists
    database_names = pymongo.MongoClient(
        config['database']['connection_url']).list_database_names()
    if content_market_name in database_names != -1:
        raise Exception("a content market with this name already exists "
                        "in the database. Either drop this database "
                        "or choose a different name")

    ##########################################################
    # Build Managers
    ##########################################################
    # build DAO and Partition Strategy
    dao = ContentMarketFactory.get_content_market_dao(config['database'])
    partition = UserPartitioningStrategyFactory.get_user_type_strategy(
        config['partitioning_strategy'])

    # Build Tweet Manager
    tweet_manager = ContentMarketTweetManager(dao)

    # Build User Manager
    user_manager = ContentMarketUserManager(dao, partition, tweet_manager)

    ##########################################################
    # Build Content Space
    ##########################################################
    # Build/Load Clustering
    if load:
        print("=================Load Clustering=================")
        clustering = pickle.load(open("kmers_clusters.pkl", "rb"))
    else:
        cluster_factory = ContentMarketClusteringFactory(
            config["clustering_method"])
        clustering = cluster_factory.get_cluster({
            "embeddings": dao.load_tweet_embeddings(),
            "num_bins": config["num_bins"]
        })
        clustering.generate_tweet_to_type()
        pickle.dump(clustering, open("kmers_clusters.pkl", "wb"))

    # Build Content Space
    content_space = ContentSpace()
    content_space.create_content_space(clustering)

    ##########################################################
    # Calculate Supply and Demand
    ##########################################################
    # define supply and demand
    mapping_spec = {
        "consumer": {
            "demand": ["original tweet"]
        },
        "producer": {
            "supply": ["retweet in community",
                       "retweet out community"]
        },
        "core node": {
            "demand": ["original tweet"],
            "supply": ["retweet in community",
                       "retweet out community"]
        }
    }
    # mapping_spec = {
    #     "consumer": {
    #         "demand": ["original tweet",
    #                    "quote in community",
    #                    "quote out community"]
    #     },
    #     "producer": {
    #         "supply": ["retweet in community",
    #                    "retweet out community"]
    #     },
    #     "core node": {
    #         "demand": ["original tweet",
    #                    "quote in community",
    #                    "quote out community"],
    #         "supply": ["retweet in community",
    #                    "retweet out community"]
    #     }
    # }

    # Build Mapping Manager
    mapping_manager = ContentMappingManager(content_space, user_manager,
                                            timedelta(days=30), mapping_spec)

    # Calculate Aggregate Supply and Demand
    mapping_manager.calculate_type_demand()
    mapping_manager.calculate_type_supply()
    mapping_manager.calculate_agg_mapping()

    ##########################################################
    # Write Mapping Manager to Database
    ##########################################################
    # dao.write_mapping_manager(content_market_name, mapping_manager)

    ##########################################################
    # Plotting
    ##########################################################
    kmers_plotter = KmersPlotter()
    kmers_plotter.create_mapping_curves(mapping_manager, True)

    return mapping_manager


if __name__ == '__main__':
    args = sys.argv[1:]
    args = ["kmers_mapping_supply_only", "../config.json"]
    content_market_name = args[0]
    config_file_path = args[1]

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    print("Building content market...")

    mapping_manager = build_content_market(content_market_name, config,
                                           load=True)

    # Plot causality
    mapping_causality = MappingCausalityAnalysis(mapping_manager)
    lags = list(range(1, 5))
    mapping_causality.mapping_cause_all(lags)
    mapping_causality.mapping_cause_type(lags)


    # print("Generating data plots...")

    # save_plots(content_market_name, "core_nodes", "in_community", config["num_bins"])
    # save_plots(content_market_name, "producers", "in_community", config["num_bins"])
    # save_plots(content_market_name, "consumers", "in_community", config["num_bins"])

    # save_plots(content_market_name, "core_nodes", "out_of_community", config["num_bins"])
    # save_plots(content_market_name, "producers", "out_of_community", config["num_bins"])
    # save_plots(content_market_name, "consumers", "out_of_community", config["num_bins"])

    # print("Performing and plotting PCA analysis...")

    # pca(content_market_name, config, "in_community", num_dims=2)
    # pca(content_market_name, config, "out_of_community", num_dims=2)
    # pca(content_market_name, config, "in_community", num_dims=1)
    # pca(content_market_name, config, "out_of_community", num_dims=1)

    # print("Interpreting cluster meanings...")

    # print_cluster_contents(content_market_name, config)
