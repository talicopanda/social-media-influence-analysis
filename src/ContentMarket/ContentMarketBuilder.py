from User.ContentMarketProducer import ContentMarketProducer
from User.ContentMarketConsumer import ContentMarketConsumer
from User.ContentMarketUser import ContentMarketUser
from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from ContentMarket.ContentMarketEmbedding import EmbeddingType
from User.ContentMarketCoreNode import ContentMarketCoreNode
from ContentMarket.ContentMarketClustering import ContentMarketClustering
from Tweet.ContentMarketTweet import ContentMarketTweet
from kmeans import kmer

from typing import List, Tuple, Dict
import numpy as np
import sys

sys.path.append("./user_partitioning")


class ContentMarketBuilder:
    bin_size: int
    user_partitioning_strategy: UserPartitioningStrategy
    embedding_type: EmbeddingType

    # TODO: time_frame

    def __init__(self, dao, partitioning_strategy, num_bins, embedding_type):
        self.dao = dao
        self.num_bins = num_bins
        self.user_partitioning_strategy = partitioning_strategy
        self.embedding_type = embedding_type

    # load and populate each user
    # TODO: possibly return wrong type
    def build_users(self) -> Dict[int, ContentMarketUser]:
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
            tweet = ContentMarketTweet(**original_tweet)
            users[original_tweet["user_id"]].original_tweets.append(tweet)

        for quote_in_community in self.dao.load_quotes_of_in_community():
            del quote_in_community["_id"]
            tweet = ContentMarketTweet(**quote_in_community)
            users[float(
                quote_in_community["user_id"])].quotes_of_in_community.append(
                tweet)

        for quote_out_of_community in self.dao.load_quotes_of_out_community():
            del quote_out_of_community["_id"]
            tweet = ContentMarketTweet(**quote_out_of_community)
            users[float(quote_out_of_community[
                            "quote_user_id"])].quotes_of_out_community.append(
                tweet)

        for retweet_in_community in self.dao.load_retweets_of_in_community():
            del retweet_in_community["_id"]
            tweet = ContentMarketTweet(**retweet_in_community)
            users[float(retweet_in_community[
                            "user_id"])].retweets_of_in_community.append(tweet)

        for retweet_of_out_community in self.dao.load_retweets_of_out_community():
            del retweet_of_out_community["_id"]
            tweet = ContentMarketTweet(**retweet_of_out_community)
            users[float(retweet_of_out_community[
                            "retweet_user_id"])].retweets_of_out_community.append(
                tweet)

    # partition the users in the community to producers, consumer, and core nodes.
    # note that producers and consumers are not mutually exclusive
    def partition_users(self, users) -> Tuple[
        List[ContentMarketProducer], List[ContentMarketConsumer], List[
            ContentMarketCoreNode]]:
        producers = []
        consumers = []
        core_nodes = []
        for user in users:
            if user.rank < 10:  # 10 top users are core nodes
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

    def compute_producer_consumer_split(self) -> Tuple[
        List[ContentMarketProducer], List[ContentMarketConsumer]]:
        producers = []
        consumers = []
        for user in self.dao.load_users():
            if self.user_partitioning_strategy.is_producer(user):
                new_prod = ContentMarketProducer(
                    user['user_id'], self.dao, user['tweets'],
                    user['retweets_in_community'])
                producers.append(new_prod)
            if self.user_partitioning_strategy.is_consumer(user):
                new_consumer = ContentMarketConsumer(
                    user['user_id'], self.dao, user['retweets'])
                consumers.append(new_consumer)

        return (producers, consumers)

    def compute_bins(self) -> ContentMarketClustering:
        embeddings = self.dao.load_tweet_embeddings()

        data = np.asarray(list(embeddings.values()), dtype=np.float32)

        clusters, centers, radius = kmer(data, self.num_bins)

        ids = list(embeddings.keys())

        assert (len(data) == len(ids) == len(clusters))

        tweet_to_cluster = {}
        for i in range(len(ids)):
            cluster_id = clusters[i]
            tweet_to_cluster[str(ids[i])] = int(cluster_id)

        cluster_centers = {}
        for i in range(len(centers)):
            cluster_centers[str(i)] = centers[i].tolist()

        return ContentMarketClustering(tweet_to_cluster, cluster_centers,
                                       radius)

# support = {}
#        for i in range(len(ids)):
#             cluster_id = clusters[i]

#             if cluster_id in support:
#                 entry = support[cluster_id]
#                 entry.tweet_ids.append(ids[i])

#                 dist_to_center = linalg.norm(data[i] - centers[cluster_id])
#                 if dist_to_center > entry.furthest_tweet_dist:
#                     # update furthest tweet
#                     entry.furthest_tweet = ids[i]
#                     entry.furthest_tweet_dist = dist_to_center

#                 if dist_to_center < entry.closest_tweet_dist:
#                     # update closest tweet
#                     entry.closest_tweet = ids[i]
#                     entry.closest_tweet_dist = dist_to_center
#             else:
#                 support[cluster_id] = ContentMarketSupportEntry(
#                     centers[cluster_id],
#                     [ids[i]],
#                     ids[i],
#                     linalg.norm(data[i] - centers[cluster_id]),
#                     ids[i],
#                     linalg.norm(data[i] - centers[cluster_id]))

#         print(
#             f"Unassigned vectors: {len(support[-1].tweet_ids)}")
