from __future__ import annotations

from typing import DefaultDict
from collections import defaultdict
from ContentMarketUser import ContentMarketUser
from ContentMarketEmbedding import ContentMarketEmbedding
from util import calcualate_embedding_bin


class ContentMarketProducer(ContentMarketUser):
    supply: DefaultDict

    def __init__(self, user_id, dao, tweets, retweets_in_community):
        self.supply = defaultdict(list)
        self.calculate_supply(dao, tweets, retweets_in_community)
        super().__init__(user_id)

    def calculate_supply(self, dao, tweets, retweets_in_community):
        for tweet_id in tweets:
            embedding = dao.load_tweet_embedding(tweet_id)
            if embedding:
                self.supply[calcualate_embedding_bin(embedding)] = embedding
        for retweet_in_community in retweets_in_community:
            embedding = dao.load_tweet_embedding(retweet_in_community)
            if embedding:
                self.supply[calcualate_embedding_bin(embedding)] = embedding
