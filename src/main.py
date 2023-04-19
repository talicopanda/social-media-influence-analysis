import json
from user_partitioning.UserPartitioningStrategyFactory import UserPartitioningStrategyFactory
from ContentMarket.ContentMarketBuilder import ContentMarketBuilder
from DAO.ContentMarketFactory import ContentMarketFactory
from ContentMarket.ContentMarket import ContentMarket
import sys
import pickle
import pymongo
import random
import numpy as np
import bson
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

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

    db_community = pymongo.MongoClient()[config["database"]["content_market_db_name"]]
    db_clustering = pymongo.MongoClient()[content_market_name]["clustering"]

    ids_to_hashtag_count = {key: {} for key in range(-1, num_clusters)}

    tweet_to_cluster = db_clustering.find()[0]
    del tweet_to_cluster["_id"]

    collections = ["clean_original_tweets_collection", 
                    "clean_replies_collection",
                    "clean_quotes_of_in_community_collection",
                    "clean_quotes_of_out_community_collection",
                    "clean_retweets_of_in_community_collection",
                    "clean_retweets_of_out_community_collection"]

    example_tweets = [[] for _ in range(num_clusters)]

    for tweet in db_community[config["database"]["tweet_embeddings_collection"]].find({}, { "id": 1, "hashtags": 1, "_id": 0 }):
        hashtags = tweet["hashtags"]
        cluster_id = tweet_to_cluster[str(tweet["id"])]
        for hashtag in hashtags:
            if hashtag in ids_to_hashtag_count[cluster_id]:
                ids_to_hashtag_count[cluster_id][hashtag] += 1
            else:
                ids_to_hashtag_count[cluster_id][hashtag] = 0
            # if cluster_id != -1 and random.randint(0, 100) == 1:
            #     for collec in collections:
            #         for t in db_community[config["database"][collec]].find({"id": tweet["id"]}, { "text": 1 }):
            #             example_tweets[cluster_id].append(t["text"])

    del ids_to_hashtag_count[-1]

    for i in range(len(example_tweets)):
        print(f"=== Cluster {i} Sample Tweets ===")
        print(example_tweets[i])
    

    for key, val in ids_to_hashtag_count.items():
        print(f"=== Cluster {key} ({sum(val.values())} total hashtags) ===")
        top5 = [(k, v) for k, v in sorted(
            val.items(), key=lambda item: item[1], reverse=True)][:5]
        for x in top5:
            print(f"{x[0]} ({x[1]}), ", end=" ")
        print()


def pca(content_market_name, config):
    db_community = pymongo.MongoClient()[config["database"]["content_market_db_name"]][config["database"]["tweet_embeddings_collection"]]
    db_content_market = pymongo.MongoClient()[content_market_name]

    tweetid_to_index = {}
    X = []
    i = 0
    for tweet in db_community.find({}, { "id": 1, "embedding": 1, "_id": 0 }):
        tweetid_to_index[tweet["id"]] = i
        X.append(tweet["embedding"])
        i += 1

    pca = PCA(n_components=2)
    pca.fit(X)

    core_node_demand_tweet_ids = []
    core_node_supply_tweet_ids = []
    user_demand_tweet_ids = []
    user_supply_tweet_ids = []
    for user in db_content_market["core_nodes"].find():
        for demand in user["demand"].values():
            for demand_id in demand:
                core_node_demand_tweet_ids.append(tweetid_to_index[demand_id])
        for supply in user["supply"].values():
            for supply_id in supply:
                core_node_supply_tweet_ids.append(tweetid_to_index[supply_id])

    for user in db_content_market["consumers"].find():
        for demand in user["demand"].values():
            for demand_id in demand:
                user_demand_tweet_ids.append(tweetid_to_index[demand_id])

    for user in db_content_market["producers"].find():
         for supply in user["supply"].values():
            for supply_id in supply:
                user_supply_tweet_ids.append(tweetid_to_index[supply_id])

    # one_dim = pca.components_[0]
    # plt.hist(one_dim, density=False, bins=100) 
    # plt.ylabel('Frequency')
    # plt.xlabel('Content Space')
    # plt.savefig(f'../results/PCA_histogram')

    pca = PCA(n_components=2)
    pca.fit(np.transpose(np.asarray(X)))
    plt.scatter(pca.components_[0][user_supply_tweet_ids], pca.components_[1][user_supply_tweet_ids], color="red", marker="o", alpha=0.05, label="user supply")
    plt.scatter(pca.components_[0][user_demand_tweet_ids], pca.components_[1][user_demand_tweet_ids], color="blue", marker="o", alpha=0.05, label="user demand")
    plt.scatter(pca.components_[0][core_node_supply_tweet_ids], pca.components_[1][core_node_supply_tweet_ids], color="orange", marker="x", alpha=0.05, label="core_nodes supply")
    plt.scatter(pca.components_[0][core_node_demand_tweet_ids], pca.components_[1][core_node_demand_tweet_ids], color="green", marker="x", alpha=0.05, label="core_nodes demand")
    plt.legend()
    plt.savefig(f'../results/PCA_scatter')
    
    plt.clf()



if __name__ == '__main__':
    args = sys.argv[1:]
    content_market_name = args[0]
    config_file_path = args[1]

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    #build_content_market(content_market_name, config)
    
    # save_plots(content_market_name, "core_nodes", config["num_bins"])
    # save_plots(content_market_name, "producers", config["num_bins"])
    # save_plots(content_market_name, "consumers", config["num_bins"])

    # print_cluster_contents(content_market_name, config)

    pca(content_market_name, config)
    
    
