import pprint
import json
from user_partitioning.UserPartitioningStrategyFactory import UserPartitioningStrategyFactory
from ContentMarket.ContentMarketBuilder import ContentMarketBuilder
from DAO.ContentMarketFactory import ContentMarketFactory
from ContentMarket.ContentMarket import ContentMarket
import sys
import pickle
sys.path.append("DAO")
sys.path.append("user_partitioning")


def main(args):
    # TODO: add user-friendly output
    content_market_name = args[0]
    config_file_path = args[1]
    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    # pprint.pprint(config)

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


if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
