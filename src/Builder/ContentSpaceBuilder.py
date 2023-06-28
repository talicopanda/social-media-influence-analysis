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
        # create()
        # param: str, ContentSpaceMongoDAO, UserPartitioningStrategy
        if len(args) == 3:
            self.name = args[0]
            self.dao = args[1]
            self.partition = args[2]
        # load()
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

        # (4) - filtering (this is actually not necessary)
        # tweet_manager.load_tweets(self._convert_market_to_space_tweet(self.filter_original_tweets(self.market.original_tweets, self.market.retweets_of_in_comm)),
        #     TweetType.ORIGINAL_TWEET)
        # tweet_manager.load_tweets(self._convert_market_to_space_tweet(self.filter_retweets_of_in_community(self.market.original_tweets, self.market.retweets_of_in_comm)),
        #     TweetType.RETWEET_OF_IN_COMM)
        # tweet_manager.load_tweets(self._convert_market_to_space_tweet(self.filter_retweets_of_out_community(self.market.original_tweets, self.market.retweets_of_out_comm)),
        #     TweetType.RETWEET_OF_OUT_COMM)

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
            if self.mapping.get_content_type(tweet.id) is not None:  # (3) - filtering for binning
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

    def filter_original_tweets(self, original_tweets: Set[ContentMarketTweet], 
                               retweets_of_in_community: Set[ContentMarketTweet]) \
                                -> Set[ContentMarketTweet]:
        """Remove original tweets that are never retweeted in community."""
        original_ids = set()
        for tweet in retweets_of_in_community:
            original_ids.add(tweet.retweet_id)
        filtered_tweets = set()
        for tweet in original_tweets:
            if tweet.id in original_ids:
                filtered_tweets.add(tweet)
        return filtered_tweets
    
    def filter_retweets_of_in_community(self, original_tweets: Set[ContentMarketTweet], 
                                        retweets_of_in_community: Set[ContentMarketTweet]) \
                                            -> Set[ContentMarketTweet]:
        """Remove retweets of in community that do not map to an original tweet."""
        original_ids = set()
        for tweet in original_tweets:
            original_ids.add(tweet.id)
        filtered_tweets = set()
        for tweet in retweets_of_in_community:
            if tweet.retweet_id in original_ids:
                filtered_tweets.add(tweet)
        return filtered_tweets
    
    def filter_retweets_of_out_community(self, original_tweets: Set[ContentMarketTweet], 
                                         retweets_of_out_community: Set[ContentMarketTweet]) \
                                            -> Set[ContentMarketTweet]:
        """Remove retweets of out community that do not map to an original tweet."""
        original_ids = set()
        for tweet in original_tweets:
            original_ids.add(tweet.id)
        filtered_tweets = set()
        for tweet in retweets_of_out_community:
            if tweet.retweet_id in original_ids:
                filtered_tweets.add(tweet)
        return filtered_tweets
    
    # def filter_mapping(self, tweet_manager: TweetManager):
    #     original_tweet_ids = {tweet.id for tweet in tweet_manager.original_tweets}
    #     retweets_of_in_comm_ids = {tweet.id for tweet in tweet_manager.retweets_of_in_comm}
    #     retweets_of_out_comm_ids = {tweet.id for tweet in tweet_manager.retweets_of_out_comm}
    #     all_ids = original_tweet_ids.union(retweets_of_in_comm_ids.union(retweets_of_out_comm_ids))
        
    #     filtered_mapping = {}
    #     for id in self.mapping.tweet_to_type:
            