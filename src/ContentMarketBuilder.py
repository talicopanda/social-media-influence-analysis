import sys
from typing import List, Tuple
from ContentMarketProducer import ContentMarketProducer
from ContentMarketConsumer import ContentMarketConsumer
from UserTypeStrategy.UsersStrategy import UsersStrategy
from UserTypeStrategy.UserPartitioningStrategy import UserPartioningStrategy
from ContentMarketEmbedding import EmbeddingType

class ContentMarketBuilder:
    bin_size: int   
    user_partitioning_strategy: UserPartioningStrategy
    embedding_type: EmbeddingType
    # TODO: time_frame

def __init__(self, dao, bin_size, partitioning_strategy, embedding_type):
    self.dao = dao
    self.bin_size = bin_size
    self.user_partitioning_strategy = partitioning_strategy
    self.embedding_type = embedding_type
        
def compute_producer_consumer_split(self) -> Tuple[List[ContentMarketConsumer], List[ContentMarketProducer]]:
    producers = []
    consumers = []
    for user in self.dao.load_users():
        if self.user_type_strategy.is_producer(user.id):
            new_prod = ContentMarketProducer()
            producers.append(new_prod)
        if self.user_type_strategy.is_producer(user.id):
            new_consumer = ContentMarketConsumer()
            consumers.append(new_consumer)

    return (producers, consumers)

def compute_supplies(self, producers: List[ContentMarketProducer]):
    # this should be on a user object (or producer / consumer wtv)
    for producer in producers:
        producer.calculate_supply(self.dao)
        
def compute_demands(self, consumers: List[ContentMarketConsumer]):
    for consumer in consumers:
        consumer.calculate_demand(self.dao)

if __name__ == '__main__':
    args = sys.argv[1:]
    config_file_name = args[0]
    db_name = args[1]
    users_collection_name = args[2]