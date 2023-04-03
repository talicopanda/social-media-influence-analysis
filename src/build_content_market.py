import pprint
import json
from user_partitioning.UserPartitioningStrategyFactory import UserPartitioningStrategyFactory
from ContentMarket.ContentMarketBuilder import ContentMarketBuilder
from DAO.ContentMarketFactory import ContentMarketFactory
from ContentMarket.ContentMarket import ContentMarket
import sys
sys.path.append("DAO")
sys.path.append("user_partitioning")


def main():
    # TODO: add user-friendly output
    args = sys.argv[1:]
    config_file_path = args[0]
    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    pprint.pprint(config)

    dao = ContentMarketFactory.get_content_market_dao(config['database'])
    partitioning_strategy = UserPartitioningStrategyFactory.get_user_type_strategy(
        config['partitioning_strategy'])

    builder = ContentMarketBuilder(
        dao, partitioning_strategy, config['num_bins'], config['embedding_type'])
    
    users = builder.build_users()
    producers, consumers, core_nodes = builder.partition_users(users)

    # get clustering from loaded tweets
    clustering = builder.compute_bins()

    # compute supply for producers given clustering
    for producer in producers:
        producer.compute_supply(clustering)
    
    # computer demand for consumers given clustering
    for consumer in consumers:
        consumer.compute_demand(clustering)

    return ContentMarket(consumers, producers, core_nodes, clustering)


if __name__ == '__main__':
    main()
