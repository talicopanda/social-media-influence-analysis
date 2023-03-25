from typing import DefaultDict
from collections import defaultdict
from util import calcualate_embedding_bin

from ContentMarketUser import ContentMarketUser
from ContentMarketEmbedding import ContentMarketEmbedding
from DAO.ContentMarketDAO import ContentMarketDAO



class ContentMarketConsumer(ContentMarketUser):
    demand: DefaultDict # TODO: doctype here

    def __init__(self, user_id):
        self.demand = defaultdict([])
        super(user_id)
    
    def calculate_demand(self, dao: ContentMarketDAO):
        retweets = dao.get_user_retweet_ids(self.user_id)
    
        for retweet in retweets:
            embedding = dao.load_tweet_embedding(retweet.id)
            self.demand[calcualate_embedding_bin(embedding)].append(embedding)