from typing import DefaultDict, Tuple
from collections import defaultdict
from util import calcualate_embedding_bin
from ContentMarketUser import ContentMarketUser



class ContentMarketCoreNode(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here
    supply: DefaultDict

    def __init__(self, user_id, dao, tweets, retweets, retweets_in_community):
        self.demand = defaultdict(list)
        self.supply = defaultdict(list)
        self.calculate_demand(dao, retweets)
        self.calculate_supply(dao, tweets, retweets_in_community)
        super().__init__(user_id)
    
    def calculate_demand(self, dao, retweets):
        for tweet_id in retweets:
            embedding = dao.load_tweet_embedding(tweet_id)
            self.supply[calcualate_embedding_bin(embedding)] = embedding


    def calculate_supply(self, dao, tweets, retweets_in_community):
        for tweet_id in tweets:
            embedding = dao.load_tweet_embedding(tweet_id)
            self.supply[calcualate_embedding_bin(embedding)] = embedding
        for retweet_in_community in retweets_in_community:
            embedding = dao.load_tweet_embedding(retweet_in_community)
            self.supply[calcualate_embedding_bin(embedding)] = embedding