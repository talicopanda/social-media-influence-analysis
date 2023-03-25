from typing import DefaultDict
from collections import defaultdict
from ContentMarketUser import ContentMarketUser
from ContentMarketEmbedding import ContentMarketEmbedding
from DAO.ContentMarketDAO import ContentMarketDAO
from util import calcualate_embedding_bin


class ContentMarketProducer(ContentMarketUser):
    supply: DefaultDict

    def __init__(self, user_id):
        self.demand = defaultdict([])
        super(user_id)

    def calculate_supply(self, dao: ContentMarketDAO):
        tweets = dao.load_user_tweet_ids(self.user_id)
        retweets_in_community = dao.load_user_retweet_in_community_ids(self.user_id)
    
        for tweet in tweets:
            embedding = dao.get_tweet_embedding(tweet.id)
            self.supply[calcualate_embedding_bin(embedding)] = embedding
        for retweet_in_community in retweets_in_community:
            embedding = dao.get_tweet_embedding(retweet_in_community.id)
            self.supply[calcualate_embedding_bin(embedding)] = embedding
