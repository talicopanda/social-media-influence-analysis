from User.UserBase import UserBase
from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from User.UserType import UserType
from Tweet.TweetType import TweetType
from Tweet.TweetManager import TweetManager
from Tweet.TweetBase import TweetBase
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.MinimalTweet import MinimalTweet

from typing import Set, Dict, Any, List
from collections import defaultdict


class UserManager:
    # Attributes
    users: Set[UserBase]
    consumers: Set[UserBase]
    producers: Set[UserBase]
    core_nodes: Set[UserBase]

    def __init__(self, *args):
        # param: Set[UserBase], UserPartitioningStrategy, TweetManager
        if len(args) == 3:
            print("=================Build Users=================")
            # initialize variables
            self.consumers = set()
            self.producers = set()
            self.core_nodes = set()

            # build users
            self.users = args[0]

            # add tweets to user's information
            print("==============Add Tweets To Users==============")
            self._add_tweets_to_users(args[2])

            # partition user to consumer/producer/core node
            print("=================Partition Users=================")
            self._partition_users(args[1])
            print("=========Successfully Build UserManager=========")
        # param: Dict[UserType, Set[UserBase]]
        elif len(args) == 1:
            users = args[0]
            self.consumers = users[UserType.CONSUMER]
            self.producers = users[UserType.PRODUCER]
            self.core_nodes = users[UserType.CORE_NODE]
            self.users = self.consumers | self.producers | self.core_nodes

    def _partition_users(self, partition: UserPartitioningStrategy) -> None:
        """Split <users> into consumers, producers, and core nodes
        by <partition>, and store them into class variables.
        """
        for user in self.users:
            if partition.is_consumer(user):
                self.consumers.add(user)
            if partition.is_producer(user):
                self.producers.add(user)
            if partition.is_core_node(user):
                self.core_nodes.add(user)

    def _add_tweets_to_users(self, tweet_manager: TweetManager) -> None:
        """Add tweet id to each user's object variables.
        """
        # For Original Tweet
        for tweet in tweet_manager.get_type_tweets(TweetType.ORIGINAL_TWEET):
            self.get_user(tweet.user_id).original_tweets.add(tweet)

        # For Quotes of In Community
        for tweet in tweet_manager.get_type_tweets(TweetType.QUOTE_OF_IN_COMM):
            self.get_user(int(tweet.user_id)).quotes_of_in_community.add(tweet)

        # For Quotes of Out Community
        for tweet in tweet_manager.get_type_tweets(TweetType.QUOTE_OF_OUT_COMM):
            self.get_user(int(tweet.quote_user_id)).quotes_of_out_community.add(
                tweet)

        # For Retweets of In Community
        for tweet in tweet_manager.get_type_tweets(
                TweetType.RETWEET_OF_IN_COMM):
            self.get_user(int(tweet.user_id)).retweets_of_in_community.add(
                tweet)

        # For Retweets of Out Community
        for tweet in tweet_manager.get_type_tweets(
                TweetType.RETWEET_OF_OUT_COMM):
            self.get_user(
                int(tweet.retweet_user_id)).retweets_of_out_community.add(tweet)

        # For Replies
        for tweet in tweet_manager.get_type_tweets(
                TweetType.REPLY):
            self.get_user(int(tweet.user_id)).replies.add(tweet)

    def get_user(self, userid: int) -> UserBase:
        """Return a User with <userid>.
        """
        for user in self.users:
            if user.user_id == userid:
                return user

        # if this is not for any user, raise Exception
        raise Exception(f"`{userid}` is not in the list")

    def get_type_users(self, user_type: UserType) -> Set[UserBase]:
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

    def _get_user_tweets(self, user, tweet_type: TweetType) -> Set[TweetBase]:
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

    def calculate_user_time_mapping(self, user: ContentSpaceUser,
                                    tweet_types: List[TweetType]) -> \
            Dict[Any, Set[MinimalTweet]]:
        # initialize dictionary storage
        freq_dict = defaultdict(set)

        # accumulate time series (user has own ContentSpaceTweet)
        for tweet_type in tweet_types:
            for tweet in self._get_user_tweets(user, tweet_type):
                freq_dict[tweet.content.get_representation()]\
                    .add(MinimalTweet(tweet.id, tweet.created_at))

        # return dictionary
        return freq_dict
