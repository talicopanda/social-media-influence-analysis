import sys
from DAO.ContentMarketFactory import ContentMarketFactory
from ContentMarketBuilder import ContentMarketBuilder

def main():
    # TODO: move command line arguments into config file
    # TODO: parse arguements cleaner
    args = sys.argv[1:]
    db_name = args[0]
    db_type = args[1]
    users_collection_name = args[2]
    tweet_embeddings_collection_name = args[3]

    bin_size = args[4]
    partioning_strategy = args[5]
    embedding_type = args[6]

    dao = ContentMarketFactory.get_content_market_dao(db_type, db_name, users_collection_name, tweet_embeddings_collection_name)
    
    builder = ContentMarketBuilder(dao, bin_size, partioning_strategy, embedding_type)
    consumers, producers = builder.compute_producer_consumer_split()
    builder.compute_supplies(producers)
    builder.compute_demands(consumers)

    # TODO: build content market object with consumers and producers


if __name__ == '__main__':
    main()