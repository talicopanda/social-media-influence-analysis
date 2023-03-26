from typing import DefaultDict
from collections import defaultdict
from util import calcualate_embedding_bin

from ContentMarketUser import ContentMarketUser
from ContentMarketEmbedding import ContentMarketEmbedding

class ContentMarketConsumer(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here

    def __init__(self, user_id, dao, retweets):
        self.demand = defaultdict(list)
        self.calculate_demand(dao, retweets)
        super().__init__(user_id)
    
    def calculate_demand(self, dao, retweets):
        for tweet_id in retweets:
            embedding = dao.load_tweet_embedding(tweet_id)
            if embedding:
                self.demand[calcualate_embedding_bin(embedding)] = embedding
