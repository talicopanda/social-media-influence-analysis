import sys
sys.path.append("./user_partitioning")
from typing import List, Tuple, Dict
from ContentMarket.ContentMarketProducer import ContentMarketProducer
from ContentMarket.ContentMarketConsumer import ContentMarketConsumer
from ContentMarket.ContentMarketUser import ContentMarketUser
from user_partitioning.UserPartitioningStrategy import UserPartitioningStrategy
from ContentMarket.ContentMarketEmbedding import EmbeddingType
from ContentMarket.ContentMarket import ContentMarket
from ContentMarket.ContentMarketCoreNode import ContentMarketCoreNode
from ContentMarket.ContentTweet import ContentTweet

class ContentMarketBuilder:
    bin_size: int   
    user_partitioning_strategy: UserPartitioningStrategy
    embedding_type: EmbeddingType
    # TODO: time_frame

    def __init__(self, dao, partitioning_strategy, bin_size, embedding_type):
        self.dao = dao
        self.bin_size = bin_size
        self.user_partitioning_strategy = partitioning_strategy
        self.embedding_type = embedding_type

    # load and populate each user
    def build_users(self) -> List[ContentMarketUser]:
        users = {}
        for user in self.dao.load_community_users():
            # TODO: remove once naming is adjusted is given data
            user_dict = {
                "user_id": user["userid"],
                "rank": user["rank"],
                "username": user["username"],
                "influence_one": user["influence one"],
                "influence_two": user["influence two"],
                "production_utility": user["production utility"],
                "consumption_utility": user["consumption utility"],
                "local_follower_count": user["local follower"],
                "local_following_count": user["local following"],
                "local_followers": user["local follower list"],
                "local_following": user["local following list"],
                "global_follower_count": user["global follower"],
                "global_following_count": user["global following"],
                "is_new_user": user["is new user"]
            }
            new_user = ContentMarketUser(**user_dict)
            users[new_user.user_id] = new_user
        return users

    def load_tweets(self, users: Dict[str, ContentMarketUser]):
        for original_tweet in self.dao.load_original_tweets():
            del original_tweet["_id"]
            tweet = ContentTweet(**original_tweet)
            users[original_tweet["user_id"]].original_tweets.append(tweet)
        
        for quote_in_community in self.dao.load_quotes_of_in_community():
            del quote_in_community["_id"]
            tweet = ContentTweet(**quote_in_community)
            users[quote_in_community["user_id"]].quotes_of_in_community.append(tweet)
        
        for quote_out_of_community in self.dao.load_quotes_of_out_community():
            del quote_out_of_community["_id"]
            tweet = ContentTweet(**quote_out_of_community)
            users[quote_out_of_community["user_id"]].quotes_of_out_community.append(tweet)
        
        for retweet_in_community in self.dao.load_retweets_of_in_community():
            del retweet_in_community["_id"]
            tweet = ContentTweet(**retweet_in_community)
            users[retweet_in_community["user_id"]].retweets_of_in_community.append(tweet)
        
        for original_tweet in self.dao.load_retweets_of_out_community():
            del original_tweet["_id"]
            tweet = ContentTweet(**original_tweet)
            users[original_tweet["user_id"]].retweets_of_out_community.append(tweet)


    # partition the users in the community to producers, consumer, and core nodes.
    # note that producers and consumers are not mutually exclusive
    def partition_users(self, users) -> Tuple[List[ContentMarketProducer], List[ContentMarketConsumer], List[ContentMarketCoreNode]]:
        producers = []
        consumers = []
        core_nodes = []
        for user in users:
            if user.rank < 10: # 10 top users are core nodes
                core_node = ContentMarketCoreNode(**vars(user))
                core_nodes.append(core_node)
            else:
                if self.user_partitioning_strategy.is_producer(user):
                    new_prod = ContentMarketProducer(**vars(user))
                    producers.append(new_prod)
                if self.user_partitioning_strategy.is_consumer(user):
                    new_consumer = ContentMarketConsumer(**vars(user))
                    consumers.append(new_consumer)

        return (producers, consumers, core_nodes)