from DAO.DAOFactory import DAOFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Mapping.MappingFactory import MappingFactory

from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder

from TS.SimpleTimeSeriesBuilder import SimpleTimeSeriesBuilder
from TS.MATimeSeriesBuilder import MATimeSeriesBuilder
from TS.FractionTimeSeriesBuilder import FractionTimeSeriesBuilder
from TS.SupplyCentricMATimeSeriesBuilder import SupplyCentricMATimeSeriesBuilder
from TS.SupplyCentricTimeSeriesBuilder import SupplyCentricTimeSeriesBuilder
from TS.SupplyAdvanceTimeSeriesBuilder import SupplyAdvanceTimeSeriesBuilder
from TS.FractionTimeSeriesConverter import FractionTimeSeriesConverter

from Causality.CausalityAnalysisTool import *
from Causality.BinningCausalityAnalysis import BinningCausalityAnalysis
from Causality.RankCausalityAnalysis import RankCausalityAnalysis

from User.UserType import UserType
from Visualization.KmersPlotter import KmersPlotter
from Visualization.CreatorPlotter import CreatorPlotter
from Visualization.BinningPlotter import BinningPlotter

import os
import json
import pickle
from datetime import datetime, timedelta
import numpy as np
import matplotlib.pyplot as plt

#%% ###################### Parameter Setup ######################
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
SPACE_STORE = False
DEMAND_SUPPLY_STORE = False

# Skip Building
MARKET_SKIP = False
SPACE_SKIP = False

#%% ################### Build DAO Factory and Partitioning ###################
dao_factory = DAOFactory()
partition = UserPartitioningStrategyFactory.get_user_type_strategy(
    config["partitioning_strategy"])

#%% ######################### Build Content Market #########################
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

# core_node_id = 18104734
# market.preserve_core_node(core_node_id)

#%% ######################### Build Content Space #########################
if not SPACE_SKIP:
    # Build ContentType Mapping
    space_dao = dao_factory.get_content_space_dao(config["database"])
    mapping = None
    if not SPACE_LOAD:
        print("=================Creating Mapping=================")
        mapping_factory = MappingFactory(config["content_type_method"])
        mapping = mapping_factory.get_cluster({
            "num_clusters": config["num_clusters"],
            "embeddings": market_dao.load_tweet_embeddings(),
            # "words": ["chess"],
            "num_bins": config["num_bins"],
            "market": market
        })
        mapping.generate_tweet_to_type()
        pickle.dump(mapping, open("binning_mapping.pkl", "wb"))
        # mapping = pickle.load(open("binning_mapping.pkl", "rb"))
        # print("=================Loading Mapping=================")

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

#%% ######################### Build Demand and Supply #########################
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

#%% #################### Plotting ####################
# plotter = BinningPlotter(ds)
# plotter.create_mapping_curves(save=True)

#%% ######################### Build Time Series #########################
start = datetime(2020, 9, 1)
end = datetime(2023, 2, 1)
period = timedelta(days=2)
ts_builder = SupplyCentricTimeSeriesBuilder(ds, space, start, end, period, 0)
# ts_builder = FractionTimeSeriesConverter(ts_builder)

#%% Agg Supply and Demand analysis
consumer_demand = ts_builder.create_all_type_time_series(UserType.CONSUMER, "demand_in_community")
core_node_demand = ts_builder.create_all_type_time_series(UserType.CORE_NODE, "demand_in_community")
core_node_supply = ts_builder.create_all_type_time_series(UserType.CORE_NODE, "supply")
producer_supply = ts_builder.create_all_type_time_series(UserType.PRODUCER, "supply")

demand = np.add(consumer_demand, core_node_demand)
supply = np.add(producer_supply, core_node_supply)

# plot time series
plt.figure()
plt.plot(ts_builder.get_time_stamps(), demand, label="demand")
plt.plot(ts_builder.get_time_stamps(), supply, label="supply")
plt.legend()
plt.gcf().autofmt_xdate()
title = "Aggregate Supply and Demand, advance = 9 days"
plt.title(title)
plt.savefig("../results/" + title)

# Granger Causality
lags = list(range(-10, 11))
plt.figure()
gc = gc_score_for_lags(demand, supply, lags)
plt.plot(lags, gc)
plt.xticks(lags)
plt.xlabel("lags")
plt.ylabel("p-value")
plt.axhline(y=0.05, color="red", linestyle="--")
title = "granger causality for aggregate supply and demand, advance = 9 days"
plt.title(title)
plt.savefig("../results/" + title)

# Results for structural properties
from analysis import original_tweets_to_retweets_ratio, plot_social_support_rank_and_value, \
    plot_social_support_and_number_of_followers, plot_social_support_and_number_of_followings, \
    plot_rank_binned_followings, plot_bhattacharyya_distances, plot_social_support_rank_and_retweets

print("")
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