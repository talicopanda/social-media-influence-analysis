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
from Causality.CreatorCausalityAnalysis import CreatorCausalityAnalysis
from Visualization.PCAPlotter import *
from Visualization.TweetToRetweetRatio import *

import json
import sys
import pickle
import pymongo
from datetime import timedelta
import time
import matplotlib.pyplot as plt


##########################################################
# Parameter Setup
##########################################################
# retrieve configuration
start = time.time()
args = ["kmers_mapping_supply_only", "../config.json"]
content_market_name = args[0]
config_file_path = args[1]

config_file = open(config_file_path)
config = json.load(config_file)
config_file.close()

# Loading clustering/to database
LOAD_CLUSTER = True
WRITE_TO_DATABASE = False

# define supply and demand
full_mapping_spec = {
    "consumer": {
        "demand": ["retweet in community",
                   "retweet out community"]
    },
    "producer": {
        "supply": ["original tweet"]
    },
    "core node": {
        "demand": ["retweet in community",
                   "retweet out community"],
        "supply": ["original tweet"]
    }
}

# plotting_mapping_spec = {
#     "consumer": {
#         "demand": ["retweet in community"]
#     },
#     "producer": {
#         "supply": ["original tweet"]
#     },
#     "core node": {
#         "demand": ["retweet in community"],
#         "supply": ["original tweet"]
#     }
# }


##########################################################
# Database check
##########################################################
if config['database']['db_type'] != "Mongo":
    raise Exception("Unsupported database type")

# check if a content market database with the given name already exists
database_names = pymongo.MongoClient(
    config['database']['connection_url']).list_database_names()
if content_market_name in database_names != -1 and False:
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
# Build Clustering
if LOAD_CLUSTER:
    print("=================Load Clustering=================")
    clustering = pickle.load(open("kmers_clusters.pkl", "rb"))
else:
    cluster_factory = ContentMarketClusteringFactory(
        config["clustering_method"])
    clustering = cluster_factory.get_cluster({
        "embeddings": dao.load_tweet_embeddings(),
        "num_bins": config["num_bins"],
    })
    clustering.generate_tweet_to_type()
    pickle.dump(clustering, open("creator_clusters.pkl", "wb"))

# Build Content Space
content_space = ContentSpace()
content_space.create_content_space(clustering)

##########################################################
# Calculate Supply and Demand
##########################################################
# Build Mapping Manager
full_mapping_manager = ContentMappingManager(content_space, user_manager,
                                        timedelta(days=14), full_mapping_spec)
# plotting_mapping_manager = ContentMappingManager(content_space, user_manager,
#                                         timedelta(days=30), plotting_mapping_spec)

# Calculate Aggregate Supply and Demand
full_mapping_manager.calculate_type_demand()
full_mapping_manager.calculate_type_supply()
full_mapping_manager.clear_trailing_zero()
full_mapping_manager.calculate_agg_mapping()

##########################################################
# Write Mapping Manager to Database
##########################################################
if WRITE_TO_DATABASE:
    dao.write_mapping_manager(content_market_name, full_mapping_manager)


##########################################################
# Plotting
##########################################################
# KMers Plotting
# kmers_plotter = KmersPlotter()
# kmers_plotter.create_mapping_curves(full_mapping_manager, True)

##########################################################
# Causality Analysis
##########################################################
# Plot causality
# mapping_causality = MappingCausalityAnalysis(full_mapping_manager)
# # mapping_causality = CreatorCausalityAnalysis(full_mapping_manager)
# lags = list(range(1, 10))
# mapping_causality.mapping_cause_all(lags)
# # mapping_causality.mapping_cause_type(lags)

end = time.time()
print(f"elapsed {round(end - start, 3)} seconds")

consumer_demand_series = full_mapping_manager.get_agg_type_demand_series(UserType.CONSUMER)
core_node_demand_series = full_mapping_manager.get_agg_type_demand_series(UserType.CORE_NODE)
core_node_supply_series = full_mapping_manager.get_agg_type_supply_series(UserType.CORE_NODE)
producer_supply_series = full_mapping_manager.get_agg_type_supply_series(UserType.PRODUCER)
time_stamps = full_mapping_manager.time_stamps

plt.figure()
plt.plot(time_stamps, consumer_demand_series, label="consumer demand")
plt.plot(time_stamps, core_node_demand_series, label="core node demand")
plt.plot(time_stamps, core_node_supply_series, label="core node supply")
plt.plot(time_stamps, producer_supply_series, label="producer supply")
plt.legend()
plt.title("Aggregate Supply and Demand Time Series")
plt.show()
