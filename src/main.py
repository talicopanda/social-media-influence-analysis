import json
from user_partitioning.UserPartitioningStrategyFactory import UserPartitioningStrategyFactory
from ContentMarket.ContentMarketBuilder import ContentMarketBuilder
from DAO.ContentMarketFactory import ContentMarketFactory
from ContentMarket.ContentMarket import ContentMarket
import sys
import pickle
import pymongo
import matplotlib.pyplot as plt
from collections import defaultdict
import numpy as np

sys.path.append("DAO")
sys.path.append("user_partitioning")


def build_content_market(content_market_name, config):
    # TODO: add user-friendly output

    dao = ContentMarketFactory.get_content_market_dao(config['database'])
    partitioning_strategy = UserPartitioningStrategyFactory.get_user_type_strategy(
        config['partitioning_strategy'])

    builder = ContentMarketBuilder(
        dao, partitioning_strategy, config['num_bins'], config['embedding_type'])

    print("Building users...")

    users = builder.build_users()

    print("Loading tweets...")

    builder.load_tweets(users)

    print("Partitioning users...")

    producers, consumers, core_nodes = builder.partition_users(users.values())

    print("Computing bins...")

    # clustering = builder.compute_bins()
    
    # pickle.dump(clustering, open("clusters.pkl", "wb"))

    clustering = pickle.load(open("clusters.pkl", "rb"))

    print("Computing supplies...")

    # compute supply for producers given clustering
    for producer in producers:
        producer.calculate_supply(clustering)

    print("Computing demands...")

    # computer demand for consumers given clustering
    for consumer in consumers:
        consumer.calculate_demand(clustering)

    for core_node in core_nodes:
        core_node.calculate_demand(clustering)
        core_node.calculate_supply(clustering)

    # ContentMarket(consumers, producers, core_nodes, clustering)
    content_market = ContentMarket(content_market_name, consumers, producers, core_nodes, clustering)

    dao.write_content_market(content_market)


def save_plots(content_market_name, collection_name, num_clusters):
    db = pymongo.MongoClient()[content_market_name]
    aggregate_demand = {key: 0 for key in range(-1, num_clusters)}
    aggregate_supply = {key: 0 for key in range(-1, num_clusters)}

    align = "edge" if "core_nodes" in collection_name else "center"
    for user in db[collection_name].find():
        if "producers" not in collection_name:
            for key, val in user["demand"].items():
                aggregate_demand[int(key)] += len(val)

        if "consumers" not in collection_name:
            for key, val in user["supply"].items():
                aggregate_supply[int(key)] += len(val)

    del aggregate_demand[-1]
    del aggregate_supply[-1]

    w = 0.4

    plt.bar(range(num_clusters), list(aggregate_demand.values()), width=w, align=align, color='orange', label='Demand')
    plt.bar(range(num_clusters), list(aggregate_supply.values()), width=-w, align=align, color='blue', label='Supply')
    plt.xticks(range(num_clusters), list(aggregate_demand.keys()))
    plt.xlabel("Cluster ID")
    plt.ylabel("Frequency")
    if "producers" in collection_name:
        plt.title("Supply for " + collection_name)
    elif "consumers" in collection_name:
        plt.title("Demand for " + collection_name)
    else:
        plt.title("Demand and supply for " + collection_name)
        plt.legend()
    plt.savefig(f'../results/{collection_name}')
    plt.clf()

def print_cluster_contents(content_market_name, config):
    num_clusters = config["num_bins"]

    db_community = pymongo.MongoClient()[config["community_db_name"]][config["content_market_db_name"]]
    db_clustering = pymongo.MongoClient()[content_market_name]["clustering"]

    ids_to_hashtag_count = {key: defaultdict(0) for key in range(-1, num_clusters)}

    tweet_to_cluster = db_clustering.find()[0]["tweet_to_cluster"]

    for tweet in db_community.find({}, { "id": 1, "hashtags": 1, "_id": 0 }):
        hashtags = tweet["hashtags"]
        cluster_id = tweet_to_cluster[tweet["id"]]
        for hashtag in hashtags:
            ids_to_hashtag_count[cluster_id][hashtag] += 1
    
    del ids_to_hashtag_count[-1]

    for key, val in tweet_to_cluster.items():
        print(f"=== Cluster {key} ({sum(val.values())} total hashtags) ===")
        top5 = [(k, v) for k, v in sorted(
            val.items(), key=lambda item: item[1], reverse=True)][:5]
        for x in top5:
            print(f"{x[0]} ({x[1]}), ", end=" ")
        print()
        

if __name__ == '__main__':
    args = sys.argv[1:]
    content_market_name = args[0]
    config_file_path = args[1]

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    #build_content_market(content_market_name, config)
    
    save_plots(content_market_name, "core_nodes", config["num_bins"])
    save_plots(content_market_name, "producers", config["num_bins"])
    save_plots(content_market_name, "consumers", config["num_bins"])

    print_cluster_contents(content_market_name, config)
    
    
