from DAO.DAOFactory import DAOFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Mapping.MappingFactory import MappingFactory
from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder
from TS.TimeSeriesBuilder import TimeSeriesBuilder
from Causality.CreatorCausalityAnalysis import CreatorCausalityAnalysis
from Causality.KmersCausalityAnalysis import KmersCausalityAnalysis
from User.UserType import UserType
from Visualization.KmersPlotter import KmersPlotter
from Visualization.CreatorPlotter import CreatorPlotter
from Causality.CausalityAnalysisTool import *

import json
import pickle
import pymongo
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt

##########################################################
# Parameter Setup
##########################################################
# Load configuration
config_file_path = "../config.json"
config_file = open(config_file_path)
config = json.load(config_file)
config_file.close()

# Load from database
MARKET_LOAD = True
SPACE_LOAD = False
DEMAND_SUPPLY_LOAD = False

# Store to database
MARKET_STORE = False
SPACE_STORE = True
DEMAND_SUPPLY_STORE = True

# Skip Building
MARKET_SKIP = False
SPACE_SKIP = False

##########################################################
# Build DAO Factory and Partitioning
##########################################################
dao_factory = DAOFactory()
partition = UserPartitioningStrategyFactory.get_user_type_strategy(
    config["partitioning_strategy"])

##########################################################
# Build Content Market
##########################################################
if not MARKET_SKIP:
    market_dao = dao_factory.get_content_market_dao(config["database"])
    market_builder = ContentMarketBuilder(
        config["database"]["content_market_db_name"],
        market_dao, partition)
    if MARKET_LOAD:
        market = market_builder.load()
    else:
        market = market_builder.create()
        if MARKET_STORE:
            market_builder.store(market)

##########################################################
# Build Content Space
##########################################################
# Build ContentType Mapping
if not SPACE_SKIP:
    space_dao = dao_factory.get_content_space_dao(config["database"])
    mapping = None
    if not SPACE_LOAD:
        # print("=================Creating Mapping=================")
        # mapping_factory = MappingFactory(config["content_type_method"])
        # mapping = mapping_factory.get_cluster({
        #     "embeddings": space_dao.load_tweet_embeddings(),
        #     "num_clusters": config["num_clusters"],
        #     "dao": market_dao
        # })
        # mapping.generate_tweet_to_type()
        # pickle.dump(mapping, open("creator_mapping.pkl", "wb"))
        print("=================Loading Mapping=================")
        mapping = pickle.load(open("kmers_mapping.pkl", "rb"))

    # Build Content Space
    if SPACE_LOAD:
        space_builder = ContentSpaceBuilder(
            config["database"]["content_space_db_name"],
            space_dao, partition)
        space = space_builder.load()
    else:
        space_builder = ContentSpaceBuilder(
            config["database"]["content_space_db_name"],
            space_dao, partition, market, mapping)
        space = space_builder.create()
        if SPACE_STORE:
            space_builder.store(space)

##########################################################
# Build Demand and Supply
##########################################################
ds_dao = dao_factory.get_supply_demand_dao(config["database"])
if DEMAND_SUPPLY_LOAD:
    ds_builder = ContentDemandSupplyBuilder(
        config["database"]["content_demand_supply_db_name"], ds_dao)
    ds = ds_builder.load()
else:
    ds_builder = ContentDemandSupplyBuilder(
        config["database"]["content_demand_supply_db_name"], ds_dao, space)
    ds = ds_builder.create()
    if DEMAND_SUPPLY_STORE:
        ds_builder.store(ds)

##########################################################
# Plotting
##########################################################
plotter = KmersPlotter(ds)
plotter.create_mapping_curves(False)

##########################################################
# Build Time Series
##########################################################
start = datetime(2020, 6, 29)
end = datetime(2023, 3, 20)
period = timedelta(days=7)
ts_builder = TimeSeriesBuilder(ds, start, end, period)

##########################################################
# Build Causality Analysis
##########################################################
lags = list(range(1, 20))
ca = KmersCausalityAnalysis(ts_builder, lags)

cluster_list = [2, 5, 9, 10, 12, 16, 19]
ca.plot_cause_forward(cluster_list)
ca.plot_cause_backward(cluster_list)
