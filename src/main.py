from DAO.DAOFactory import DAOFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Mapping.MappingFactory import MappingFactory
from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder

import json
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

# Loading mapping/to database
MARKET_LOAD = False
SPACE_LOAD = False
DEMAND_SUPPLY_LOAD = False


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
# Build Content Market
##########################################################
dao_factory = DAOFactory()
market_dao = dao_factory.get_content_market_dao(config["database"])
partition = UserPartitioningStrategyFactory.get_user_type_strategy(
    config["partitioning_strategy"])
market_builder = ContentMarketBuilder(config["database"]["content_market_db_name"],
                                      market_dao, partition)
if MARKET_LOAD:
    market = market_builder.load()
else:
    market = market_builder.create()
    market_builder.store(market)


##########################################################
# Build Content Space
##########################################################
# Build Mapping
space_dao = dao_factory.get_content_space_dao(config["database"])
mapping = None
if not SPACE_LOAD:
    print("=================Load Mapping=================")
    # mapping_factory = MappingFactory(config["clustering_method"])
    # mapping = mapping_factory.get_cluster({
    #     # "embeddings": space_dao.load_tweet_embeddings(),
    #     "num_bins": config["num_bins"],
    #     "dao": market_dao
    # })
    # mapping.generate_tweet_to_type()
    # pickle.dump(mapping, open("creator_mapping.pkl", "wb"))
    mapping = pickle.load(open("creator_mapping.pkl", "rb"))

# Build Content Space
space_builder = ContentSpaceBuilder(config["database"]["content_space_db_name"],
                                    space_dao, partition, market, mapping)
if SPACE_LOAD:
    space = space_builder.load()
else:
    space = space_builder.create()
    space_builder.store(space)

##########################################################
# Build Demand and Supply
##########################################################
ds_dao = dao_factory.get_supply_demand_dao(config["database"])
ds_builder = ContentDemandSupplyBuilder(config["database"]["content_demand_supply_db_name"],
                                        ds_dao, space, timedelta(days=14))
if DEMAND_SUPPLY_LOAD:
    ds = ds_builder.load()
else:
    ds = ds_builder.create()
    ds_builder.store(ds)

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

# end = time.time()
# print(f"elapsed {round(end - start, 3)} seconds")
#
# consumer_demand_series = full_mapping_manager.get_agg_type_demand_series(UserType.CONSUMER)
# core_node_demand_series = full_mapping_manager.get_agg_type_demand_series(UserType.CORE_NODE)
# core_node_supply_series = full_mapping_manager.get_agg_type_supply_series(UserType.CORE_NODE)
# producer_supply_series = full_mapping_manager.get_agg_type_supply_series(UserType.PRODUCER)
# time_stamps = full_mapping_manager.time_stamps
#
# plt.figure()
# plt.plot(time_stamps, consumer_demand_series, label="consumer demand")
# plt.plot(time_stamps, core_node_demand_series, label="core node demand")
# plt.plot(time_stamps, core_node_supply_series, label="core node supply")
# plt.plot(time_stamps, producer_supply_series, label="producer supply")
# plt.legend()
# plt.title("Aggregate Supply and Demand Time Series")
# plt.show()
