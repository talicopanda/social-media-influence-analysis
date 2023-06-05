from User.ContentMarketUser import ContentMarketUser
from User.ContentMarketConsumer import ContentMarketConsumer
from User.ContentMarketProducer import ContentMarketProducer
from User.ContentMarketCoreNode import ContentMarketCoreNode
from UserPartitioning.UsersStrategy import UsersStrategy
from DAO.ContentMarketDAO import ContentMarketDAO
from User.UserType import UserType
from Tweet.TweetType import TweetType
from Clustering.ContentMarketClustering import ContentMarketClustering
from ContentSpace.ContentSpace import ContentSpace
from Tweet.ContentMarketTweetManager import ContentMarketTweetManager
from Tweet.ContentMarketTweet import ContentMarketTweet

from typing import Set, Dict, Any, List
from datetime import datetime


class ContentMarketUserManager:
    # Attributes
    users: Set[ContentMarketUser]
    consumers: Set[ContentMarketConsumer]
    producers: Set[ContentMarketProducer]
    core_nodes: Set[ContentMarketCoreNode]

    def __init__(self, dao: ContentMarketDAO, partition: UsersStrategy,
                 tweet_manager: ContentMarketTweetManager):
        print("=================Build Users=================")
        # initialize variables
        self.consumers = set()
        self.producers = set()
        self.core_nodes = set()

        # build users
        self.users = self._build_users(dao)

        # add tweets to user's information
        print("==============Add Tweets To Users==============")
        self._add_tweets_to_users(tweet_manager)

        # partition user to consumer/producer/core node
        print("=================Partition Users=================")
        self._partition_users(partition)

        print("=========Successfully Build UserManager=========")

    def _build_users(self, dao: ContentMarketDAO) -> Set[ContentMarketUser]:
        users = set()
        for user in dao.load_community_users():
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
            users.add(new_user)
        return users

    def _partition_users(self, partition: UsersStrategy) -> None:
        """Split <users> into consumers, producers, and core nodes
        by <partition>, and store them into class variables.
        """
        for user in self.users:
            if user.rank < 10:  # 10 top users are core nodes
                core_node = ContentMarketCoreNode(**vars(user))
                self.core_nodes.add(core_node)
            else:
                # the rest ordinary user are consumer/producer
                if partition.is_producer(user):
                    new_producer = ContentMarketProducer(**vars(user))
                    self.producers.add(new_producer)
                if partition.is_consumer(user):
                    new_consumer = ContentMarketConsumer(**vars(user))
                    self.consumers.add(new_consumer)

    def _add_tweets_to_users(self,
                             tweet_manager: ContentMarketTweetManager) -> None:
        """Add tweet id to each user's object variables.
        """
        # For Original Tweet
        for tweet in tweet_manager.get_type_tweets(TweetType.ORIGINAL_TWEET):
            self.get_user(tweet.user_id).original_tweets.add(tweet)

        # For Quotes of In Community
        for tweet in tweet_manager.get_type_tweets(TweetType.QUOTE_OF_IN_COMM):
            self.get_user(int(tweet.user_id)). \
                quotes_of_in_community.add(tweet)

        # For Quotes of Out Community
        for tweet in tweet_manager.get_type_tweets(TweetType.QUOTE_OF_OUT_COMM):
            self.get_user(int(tweet.quote_user_id)). \
                quotes_of_out_community.add(tweet)

        # For Retweets of In Community
        for tweet in tweet_manager.get_type_tweets(
                TweetType.RETWEET_OF_IN_COMM):
            self.get_user(int(tweet.user_id)). \
                retweets_of_in_community.add(tweet)

        # For Retweets of Out Community
        for tweet in tweet_manager.get_type_tweets(
                TweetType.RETWEET_OF_OUT_COMM):
            self.get_user(int(tweet.retweet_user_id)). \
                retweets_of_out_community.add(tweet)

        # For Replies
        # TODO: Remove later
        for tweet in tweet_manager.get_type_tweets(
                TweetType.REPLY):
            self.get_user(int(tweet.user_id)). \
                replies.add(tweet)


    def get_user(self, userid: int) -> ContentMarketUser:
        """Return a User with <userid>.
        """
        for user in self.users:
            if user.user_id == userid:
                return user

        # if this is not for any user, raise Exception
        raise Exception(f"`{userid}` is not in the list")

    def get_type_users(self, user_type: UserType) -> Set[ContentMarketUser]:
        """Return a set of all users of Type <user_type>.
        """
        if user_type == UserType.CONSUMER:
            return self.consumers
        elif user_type == UserType.PRODUCER:
            return self.producers
        elif user_type == UserType.CORE_NODE:
            return self.core_nodes
        else:
            raise Exception(f"Invalid User Type `{user_type}`")

    def _get_user_tweets(self, user, tweet_type: TweetType) -> Set[ContentMarketTweet]:
        """Return a list of Tweet for user with <userid> of
        type <tweet_type>.
        """
        if tweet_type == TweetType.ORIGINAL_TWEET:
            return user.original_tweets
        elif tweet_type == TweetType.QUOTE_OF_IN_COMM:
            return user.quotes_of_in_community
        elif tweet_type == TweetType.QUOTE_OF_OUT_COMM:
            return user.quotes_of_out_community
        elif tweet_type == TweetType.RETWEET_OF_IN_COMM:
            return user.retweets_of_in_community
        elif tweet_type == TweetType.RETWEET_OF_OUT_COMM:
            return user.retweets_of_out_community
        elif tweet_type == TweetType.REPLY:
            return user.replies
        else:
            raise Exception(f"Invalid Tweet Type `{tweet_type}` when getting")

    def calculate_mapping(self, clustering: ContentMarketClustering) -> None:
        """Summarize supply and demand information in each user (regardless of
        creation time period).
        """
        # Consumers
        print("=================Calculate Consumer Mapping=================")
        for consumer in self.consumers:
            consumer.calculate_demand(clustering)

        # Producers
        print("=================Calculate Producer Mapping=================")
        for producer in self.producers:
            producer.calculate_supply(clustering)

        # Core Nodes
        print("================Calculate Core Node Mapping================")
        for core_node in self.core_nodes:
            core_node.calculate_demand(clustering)
            core_node.calculate_supply(clustering)

    def calculate_time_mapping(self, user_type: UserType,
                               time_stamps: List[datetime],
                               content_space: ContentSpace,
                               tweet_types: List[TweetType]) -> \
            Dict[Any, List[int]]:
        len_time = len(time_stamps)
        # initialize dictionary storage
        freq_dict = {}
        for content_type in content_space.get_all_content_types():
            freq_dict[content_type.get_representation()] = \
                [0 for _ in range(len_time)]

        # accumulate time series (user has own ContentMarketTweet)
        for user in self.get_type_users(user_type):
            for tweet_type in tweet_types:
                for tweet in self._get_user_tweets(user, tweet_type):
                    create_time = tweet.created_at
                    representation = content_space.get_tweet_content_type_repr(int(tweet.id))
                    index = self._find_time_index(create_time, time_stamps, len_time)
                    freq_dict[representation][index] += 1

        # return dictionary
        return freq_dict

    def _find_time_index(self, create_time: datetime,
                         time_stamps: List[datetime], len_time: int) -> int:
        for i in range(len_time):
            if create_time < time_stamps[i]:
                return i - 1
