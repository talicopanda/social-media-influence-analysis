import sys
sys.path.append("./user_partitioning")
from typing import List, Tuple
from ContentMarketProducer import ContentMarketProducer
from ContentMarketConsumer import ContentMarketConsumer
from user_partitioning.UserPartitioningStrategy import UserPartioningStrategy
from ContentMarketEmbedding import EmbeddingType

class ContentMarketBuilder:
    bin_size: int   
    user_partitioning_strategy: UserPartioningStrategy
    embedding_type: EmbeddingType
    # TODO: time_frame

    def __init__(self, dao, partitioning_strategy, bin_size, embedding_type):
        self.dao = dao
        self.bin_size = bin_size
        self.user_partitioning_strategy = partitioning_strategy
        self.embedding_type = embedding_type
        
    def compute_producer_consumer_split(self) -> Tuple[List[ContentMarketProducer], List[ContentMarketConsumer]]:
        producers = []
        consumers = []
        for user in self.dao.load_users():
            if self.user_partitioning_strategy.is_producer(user):
                new_prod = ContentMarketProducer(user['user_id'], self.dao, user['tweets'], user['retweets_in_community'])
                producers.append(new_prod)
            if self.user_partitioning_strategy.is_consumer(user):
                new_consumer = ContentMarketConsumer(user['user_id'], self.dao, user['retweets'])
                consumers.append(new_consumer)

        return (producers, consumers)