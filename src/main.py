from DAO.DAOFactory import DAOFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Mapping.MappingFactory import MappingFactory

from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder
from TS.TimeSeriesBuilder import TimeSeriesBuilder

from Causality.CreatorCausalityAnalysis import CreatorCausalityAnalysis
from Causality.KmersCausalityAnalysis import KmersCausalityAnalysis
from Causality.BinningCausalityAnalysis import BinningCausalityAnalysis

from User.UserType import UserType
from Visualization.KmersPlotter import KmersPlotter
from Visualization.CreatorPlotter import CreatorPlotter
from Causality.CausalityAnalysisTool import *

import json
import pickle
from datetime import datetime, timedelta
import time
import matplotlib.pyplot as plt
import numpy as np

##########################################################
# Parameter Setup
##########################################################
# Load configuration
config_file_path = "../config.json"
config_file = open(config_file_path)
config = json.load(config_file)
config_file.close()

# Load from database
MARKET_LOAD = False
SPACE_LOAD = False
DEMAND_SUPPLY_LOAD = False

# Store to database
MARKET_STORE = False
SPACE_STORE = False
DEMAND_SUPPLY_STORE = False

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
        print("=================Creating Mapping=================")
        mapping_factory = MappingFactory(config["content_type_method"])
        mapping = mapping_factory.get_cluster({
            "num_clusters": config["num_clusters"],
            "dao": market_dao,
            "words": ["chess"],
            "embeddings": market_dao.load_tweet_embeddings(),
            "num_bins": config["num_bins"],
            "market": market
        })
        mapping.generate_tweet_to_type()
        pickle.dump(mapping, open("words_any_chess_mapping.pkl", "wb"))
        # print("=================Loading Mapping=================")
        # mapping = pickle.load(open("words_any_chess_mapping.pkl", "rb"))
        # mapping.generate_tweet_to_type()

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
# plotter = KmersPlotter(ds)
# plotter.create_mapping_curves(False)

##########################################################
# Build Time Series
##########################################################
start = datetime(2020, 6, 1)
end = datetime(2023, 5, 1)
period = timedelta(days=30)
window = timedelta(days=15)
ts_builder = TimeSeriesBuilder(ds, space, start, end, period, window)


##########################################################
# Build Causality Analysis
##########################################################
# lags = list(range(1, 10))
# ca = BinningCausalityAnalysis(ts_builder, lags)
#
# cluster_list = [1]
# ca.plot_cause_forward(cluster_list, save=True)
# ca.plot_cause_backward(cluster_list, save=True)

###########################################################################
# cluster = 1
# plt.figure()
# a = ts_builder.create_time_series(UserType.CONSUMER, cluster, "demand_in_community")
# b = ts_builder.create_time_series(UserType.CORE_NODE, cluster, "demand_in_community")
# plt.plot(ts_builder.time_stamps[:-1], np.add(a, b), label="aggregate demand")
# d = ts_builder.create_time_series(UserType.PRODUCER, cluster, "supply")
# plt.plot(ts_builder.time_stamps[:-1], d, label="producer supply")
# plt.title("chess, period = 7 days")
# plt.legend()
# plt.gcf().autofmt_xdate()
# plt.savefig("../results/aggregate demand core node supply chess 7d")
# plt.show()

from analysis import original_tweets_to_retweets_ratio, plot_social_support_rank_and_value, \
    plot_social_support_and_number_of_followers, plot_social_support_and_number_of_followings, \
    plot_rank_binned_followings, plot_bhattacharyya_distances, plot_social_support_rank_and_retweets

original_tweets_to_retweets_ratio(market)

plot_social_support_rank_and_value(space, [False, False, False, True])
plot_social_support_and_number_of_followers(space)
plot_social_support_and_number_of_followings(space)
plot_rank_binned_followings(space, bin_size=20, log=False)
plot_social_support_rank_and_value(space, [True, True, False, False])
print(len(space.retweets_of_in_comm))
print(len(space.retweets_of_out_comm_by_in_comm))
plot_social_support_rank_and_retweets(space)

# Bhattacharyya
plot_bhattacharyya_distances(space, ds)