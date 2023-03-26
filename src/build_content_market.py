import sys
sys.path.append("DAO")
sys.path.append("user_partitioning")
from DAO.ContentMarketFactory import ContentMarketFactory
from ContentMarketBuilder import ContentMarketBuilder
from user_partitioning.UserPartitioningStrategyFactory import UserPartitioningStrategyFactory
import json
import pprint

def main():
    # TODO: add user-friendly output
    args = sys.argv[1:]
    config_file_path = args[0]
    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    pprint.pprint(config)

    dao = ContentMarketFactory.get_content_market_dao(config['database'])
    partitioning_strategy = UserPartitioningStrategyFactory.get_user_type_strategy(config['partitioning_strategy'])
    
    builder = ContentMarketBuilder(dao, partitioning_strategy, config['bin_size'], config['embedding_type'])
    producers, consumers = builder.compute_producer_consumer_split()
    print("Consumers: ", consumers)
    print("Producers: ", producers)
    
    print("num failed to load", dao.failed_to_load)

    for consumer in consumers:
        if len(consumer.demand) > 0:
            print(len(consumer.demand))

    for producer in producers:
        if len(producer.supply) > 0:
            print(len(producer.supply))
    
    print(producers[0].supply)


    # TODO: build content market object with consumers and producers


if __name__ == '__main__':
    main()