from DAO.ContentMarketFactory import ContentMarketFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Tweet.ContentMarketTweetManager import ContentMarketTweetManager
from User.ContentMarketUserManager import ContentMarketUserManager
from Clustering.ContentMarketClusteringFactory import ContentMarketClusteringFactory
from ContentSpace.ContentSpace import ContentSpace
from ContentMarket.ContentMappingManager import ContentMappingManager
from Visualization.MappingPlotter import *

import json
import sys
import pickle
import pymongo
from analysis import *
from datetime import timedelta


def build_content_market(content_market_name, config, load = False):
    ##########################################################
    # Pre check
    ##########################################################
    if config['database']['db_type'] != "Mongo":
        raise Exception("Unsupported database type")

    # check if a content market database with the given name already exists
    database_names = pymongo.MongoClient(config['database']['connection_url']).list_database_names()
    if content_market_name in database_names != -1:
        raise Exception("a content market with this name already exists "
                        "in the database. Either drop this database "
                        "or choose a different name")

    ##########################################################
    # Build Managers
    ##########################################################
    # build DAO and Partition Strategy
    dao = ContentMarketFactory.get_content_market_dao(config['database'])
    partition = UserPartitioningStrategyFactory.get_user_type_strategy(config['partitioning_strategy'])

    # Build Tweet Manager
    tweet_manager = ContentMarketTweetManager(dao)

    # Build User Manager
    user_manager = ContentMarketUserManager(dao, partition, tweet_manager)

    ##########################################################
    # Build Content Space
    ##########################################################
    # Build/Load Clustering
    clustering = None
    if load:
        print("=================Load Clustering=================")
        clustering = pickle.load(open("clusters.pkl", "rb"))
    else:
        cluster_factory = ContentMarketClusteringFactory(
            config["clustering_method"])
        clustering = cluster_factory.get_cluster({
            "embeddings": dao.load_tweet_embeddings(),
            "num_bins": config["num_bins"]
        })
        clustering.generate_tweet_to_type()
        pickle.dump(clustering, open("clusters.pkl", "wb"))

    # Build Content Space
    content_space = ContentSpace()
    content_space.create_content_space(clustering)

    ##########################################################
    # Calculate Supply and Demand
    ##########################################################
    # Calculate individual supply and demand
    # user_manager.calculate_mapping(clustering) # might not need

    # Build Mapping Manager
    mapping_manager = ContentMappingManager(content_space, user_manager,
                                            timedelta(days=30))

    # Calculate Aggregate Supply and Demand
    mapping_manager.calculate_type_demand()
    mapping_manager.calculate_type_supply()
    mapping_manager.calculate_agg_mapping()

    ##########################################################
    # Plotting
    ##########################################################
    create_mapping_curves(mapping_manager)

    # builder = ContentMarketBuilder(
    #     dao, partitioning_strategy, config['num_bins'], config['embedding_type'])
    #
    # print("Building users...")
    #
    # users = builder.build_users()
    #
    # print("Loading tweets...")
    #
    # builder.load_tweets(users)
    #
    # print("Partitioning users...")
    #
    # producers, consumers, core_nodes = builder.partition_users(users.values())
    #
    # print("Computing bins...")
    #
    # clustering = 0
    # if load:
    #     clustering = pickle.load(open("clusters.pkl", "rb"))
    # else:
    #     clustering = builder.compute_bins()
    #     pickle.dump(clustering, open("clusters.pkl", "wb"))
    #
    # print("Computing supplies...")
    #
    # # compute supply for producers given clustering
    # for producer in producers:
    #     producer.calculate_supply(clustering)
    #
    # print("Computing demands...")
    #
    # # computer demand for consumers given clustering
    # for consumer in consumers:
    #     consumer.calculate_demand(clustering)
    #
    # for core_node in core_nodes:
    #     core_node.calculate_demand(clustering)
    #     core_node.calculate_supply(clustering)
    #
    # content_market = ContentMarket(content_market_name, consumers, producers, core_nodes, clustering)
    #
    # dao.write_content_market(content_market)
    return mapping_manager


if __name__ == '__main__':
    args = sys.argv[1:]
    args = ["new_chess_content_market", "../config.json"]
    content_market_name = args[0]
    config_file_path = args[1]

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    print("Building content market...")

    build_content_market(content_market_name, config, load=True)

    # print("Generating data plots...")
    #
    # save_plots(content_market_name, "core_nodes", "in_community", config["num_bins"])
    # save_plots(content_market_name, "producers", "in_community", config["num_bins"])
    # save_plots(content_market_name, "consumers", "in_community", config["num_bins"])
    #
    # save_plots(content_market_name, "core_nodes", "out_of_community", config["num_bins"])
    # save_plots(content_market_name, "producers", "out_of_community", config["num_bins"])
    # save_plots(content_market_name, "consumers", "out_of_community", config["num_bins"])
    #
    # print("Performing and plotting PCA analysis...")
    #
    # pca(content_market_name, config, "in_community", num_dims=2)
    # pca(content_market_name, config, "out_of_community", num_dims=2)
    # pca(content_market_name, config, "in_community", num_dims=1)
    # pca(content_market_name, config, "out_of_community", num_dims=1)
    #
    # print("Interpreting cluster meanings...")
    #
    # print_cluster_contents(content_market_name, config)



