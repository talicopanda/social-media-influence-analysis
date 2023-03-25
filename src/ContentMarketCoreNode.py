from typing import DefaultDict, Tuple
from collections import defaultdict
from util import calcualate_embedding_bin
from ContentMarketUser import ContentMarketUser
from DAO.ContentMarketDAO import ContentMarketDAO



class ContentMarketCoreNode(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here
    supply: DefaultDict

    def __init__(self, user_id):
        self.demand = defaultdict([])
        super(user_id)
    
    def calculate_demand(self, dao: ContentMarketDAO):
        retweets = dao.get_user_retweets(self.user_id)
    
        for retweet in retweets:
            embedding = dao.get_tweet_embedding(retweet.id)
            self.demand[calcualate_embedding_bin(embedding)].append(embedding)

    def calculate_supply(self, dao: ContentMarketDAO):
        tweet_ids = dao.load_user_tweet_ids(self.user_id)
        retweets_in_community = dao.load_user_retweet_in_community_ids(self.user_id)

        for tweet in tweets:
            embedding = dao.get_tweet_embedding(tweet.id)
            self.supply[calcualate_embedding_bin(embedding)] = embedding
        for retweet_in_community in retweets_in_community:
            embedding = dao.get_tweet_embedding(retweet_in_community.id)
            self.supply[calcualate_embedding_bin(embedding)] = embedding
