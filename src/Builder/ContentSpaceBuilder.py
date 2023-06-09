from Builder.BuilderBase import BuilderBase
from Tweet.TweetManager import TweetManager
from Tweet.TweetType import TweetType
from DAO.ContentSpaceMongoDAO import ContentSpaceMongoDAO
from User.UserManager import UserManager
from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from Aggregation.ContentMarket import ContentMarket
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from Aggregation.ContentSpace import ContentSpace
from Mapping.ContentTypeMapping import ContentTypeMapping
from Tweet.ContentMarketTweet import ContentMarketTweet
from User.ContentMarketUser import ContentMarketUser

from typing import Set


class ContentSpaceBuilder(BuilderBase):
    name: str
    dao: ContentSpaceMongoDAO
    partition: UserPartitioningStrategy
    market: ContentMarket
    mapping: ContentTypeMapping

    def __init__(self, *args):
        # param: str, ContentSpaceMongoDAO, UserPartitioningStrategy
        if len(args) == 3:
            self.name = args[0]
            self.dao = args[1]
            self.partition = args[2]
        # param: str, ContentSpaceMongoDAO, UserPartitioningStrategy,
        #        ContentMarket, ContentTypeMapping
        elif len(args) == 5:
            self.name = args[0]
            self.dao = args[1]
            self.partition = args[2]
            self.market = args[3]
            self.mapping = args[4]

    def create(self) -> ContentSpace:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self._convert_market_to_space_tweet(
            self.market.original_tweets),
            TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self._convert_market_to_space_tweet(
            self.market.retweets_of_in_comm),
            TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self._convert_market_to_space_tweet(
            self.market.retweets_of_out_comm),
            TweetType.RETWEET_OF_OUT_COMM)

        # Build User Manager
        users = self.market.consumers | self.market.producers | self.market.core_nodes
        user_manager = UserManager(self._convert_market_to_space_user(users),
                                   self.partition, tweet_manager)

        # Build Content Space
        content_space = ContentSpace(self.name, user_manager, tweet_manager)
        return content_space

    def store(self, aggregation: ContentSpace) -> None:
        super().store(aggregation)
        self.dao.store_content_space(aggregation.content_space)

    def _store_users(self, users: Set[ContentSpaceUser]) -> None:
        self.dao.store_users(users)

    def _store_tweets(self, tweets: Set[ContentSpaceTweet],
                      tweet_type: TweetType) -> None:
        self.dao.store_tweets(tweets, tweet_type)

    def load(self) -> ContentSpace:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self.dao.load_original_tweets(),
                                  TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self.dao.load_retweets_of_in_community(),
                                  TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self.dao.load_retweets_of_out_community(),
                                  TweetType.RETWEET_OF_OUT_COMM)

        # Build User Manager
        user_manager = UserManager(self.dao.load_users(),
                                   self.partition, tweet_manager)

        # Build Content Space
        return ContentSpace(self.name, user_manager, tweet_manager)

    def _convert_market_to_space_tweet(self, tweets: Set[ContentMarketTweet]) \
            -> Set[ContentSpaceTweet]:
        new_tweets = set()
        for tweet in tweets:
            tweet_dict = vars(tweet)
            tweet_dict["text"] = self.mapping.get_content_type(tweet.id)
            tweet_dict.pop("content")
            new_tweets.add(ContentSpaceTweet(**tweet_dict))
        return new_tweets

    def _convert_market_to_space_user(self, users: Set[ContentMarketUser]) \
            -> Set[ContentSpaceUser]:
        new_users = set()
        for user in users:
            user_dict = vars(user)
            user_dict["original_tweets"] = set()
            user_dict["retweets_of_in_community"] = set()
            user_dict["retweets_of_out_community"] = set()
            new_users.add(ContentSpaceUser(**user_dict))
        return new_users
