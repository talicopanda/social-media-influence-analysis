from Builder.BuilderBase import BuilderBase
from Tweet.TweetManager import TweetManager
from Tweet.TweetType import TweetType
from DAO.ContentMarketMongoDAO import ContentMarketMongoDAO
from User.UserManager import UserManager
from UserPartitioning.UserPartitioningStrategy import UserPartitioningStrategy
from Aggregation.ContentMarket import ContentMarket
from User.ContentMarketUser import ContentMarketUser
from Tweet.ContentMarketTweet import ContentMarketTweet

from typing import Set, List, Tuple

from copy import deepcopy
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer


class ContentMarketBuilder(BuilderBase):
    name: str
    dao: ContentMarketMongoDAO
    partition: UserPartitioningStrategy

    def __init__(self, name: str, dao: ContentMarketMongoDAO,
                 partition: UserPartitioningStrategy):
        self.name = name
        self.dao = dao
        self.partition = partition

    def create(self) -> ContentMarket:
        # Build Tweet Manager
        tweet_manager = TweetManager()
        tweet_manager.load_tweets(self.dao.load_original_tweets(), TweetType.ORIGINAL_TWEET)
        tweet_manager.load_tweets(self.dao.load_retweets_of_in_community(), TweetType.RETWEET_OF_IN_COMM)
        tweet_manager.load_tweets(self.dao.load_retweets_of_out_community(), TweetType.RETWEET_OF_OUT_COMM)

        # (4) - filtering
        # tweet_manager.load_tweets(self.filter_original_tweets(self.dao.load_original_tweets(), self.dao.load_retweets_of_in_community()), TweetType.ORIGINAL_TWEET)
        # tweet_manager.load_tweets(self.filter_retweets_of_in_community(tweet_manager.original_tweets, self.dao.load_retweets_of_in_community()),
        #                           TweetType.RETWEET_OF_IN_COMM)
        # tweet_manager.load_tweets(self.filter_retweets_of_in_community(tweet_manager.original_tweets, self.dao.load_retweets_of_out_community()),
        #                           TweetType.RETWEET_OF_OUT_COMM)

        # (4A) - filter and remove 0 rows based on threshold
        # original_tweets, retweets_of_in_comm, retweets_of_out_comm \
        #     = self.filter_uncommon_word_only_tweets(list(self.dao.load_original_tweets()), 
        #                                             list(self.dao.load_retweets_of_in_community()), 
        #                                             list(self.dao.load_retweets_of_out_community()))
        # # print(len(original_tweets))
        # # print(len(retweets_of_in_comm))
        # # print(len(retweets_of_out_comm))
        # # print(len(original_tweets) + len(retweets_of_in_comm) + len(retweets_of_out_comm))
        # original_tweets = self.filter_original_tweets(self.dao.load_original_tweets(), self.dao.load_retweets_of_in_community())
        # retweets_of_in_comm = self.filter_retweets_of_in_community(tweet_manager.original_tweets, self.dao.load_retweets_of_in_community())
        # retweets_of_out_comm = self.filter_retweets_of_in_community(tweet_manager.original_tweets, self.dao.load_retweets_of_out_community())

        # original_tweets, retweets_of_in_comm, retweets_of_out_comm \
        #     = self.filter_uncommon_word_only_tweets(list(original_tweets), 
        #                                             list(retweets_of_in_comm), 
        #                                             list(retweets_of_out_comm))
        # tweet_manager.load_tweets(original_tweets, TweetType.ORIGINAL_TWEET)
        # tweet_manager.load_tweets(retweets_of_in_comm,
        #                           TweetType.RETWEET_OF_IN_COMM)
        # tweet_manager.load_tweets(retweets_of_out_comm,
        #                           TweetType.RETWEET_OF_OUT_COMM)

        # Build User Manager
        user_manager = UserManager(self.dao.create_users(),
                                   self.partition, tweet_manager)

        # Build Content Market
        return ContentMarket(self.name, user_manager, tweet_manager)

    def _store_users(self, users: Set[ContentMarketUser]) -> None:
        self.dao.store_users(users)

    def _store_tweets(self, tweets: Set[ContentMarketTweet],
                      tweet_type: TweetType) -> None:
        self.dao.store_tweets(tweets, tweet_type)

    def load(self) -> ContentMarket:
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

        # Build Content Market
        return ContentMarket(self.name, user_manager, tweet_manager)
    
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

    def filter_uncommon_word_only_tweets(self, original_tweets: List[ContentMarketTweet], 
                                         retweets_of_in_comm: List[ContentMarketTweet], 
                                         retweets_of_out_comm: List[ContentMarketTweet]) \
                                            -> Tuple[Set[ContentMarketTweet], Set[ContentMarketTweet], Set[ContentMarketTweet]]:
        """..."""
        # build the corpus
        print(len(original_tweets))
        print(len(retweets_of_in_comm))
        print(len(retweets_of_out_comm))

        original_tweets_copy, retweets_of_in_comm_copy, retweets_of_out_comm_copy \
            = deepcopy(original_tweets), deepcopy(retweets_of_in_comm), deepcopy(retweets_of_out_comm)
        all_tweets = original_tweets_copy
        all_tweets.extend(retweets_of_in_comm_copy)
        all_tweets.extend(retweets_of_out_comm_copy)
        corpus = []
        tweet_boundaries = [0, len(original_tweets), 
                            len(original_tweets) + len(retweets_of_in_comm), 
                            len(original_tweets) + len(retweets_of_in_comm) + len(retweets_of_out_comm)]
        for tweet in all_tweets:
            corpus.append(tweet.content)
        
        vectorizer = CountVectorizer(min_df=0.001)
        X = vectorizer.fit_transform(corpus)
        X = X.todense()
        X = np.array(X)

        empty_docs = np.count_nonzero(X, axis=1)
        print(len(empty_docs))
        idxs_to_keep = []
        for i in range(len(empty_docs)):
            if empty_docs[i] != 0:
                idxs_to_keep.append(i)
        
        original_tweets_to_keep, retweets_of_in_comm_to_keep, retweets_of_out_comm_to_keep \
            = set(), set(), set()
        for i in range(len(all_tweets)):
            if i in idxs_to_keep:
                if i < tweet_boundaries[1]:
                    original_tweets_to_keep.add(all_tweets[i])
                elif i < tweet_boundaries[2]:
                    retweets_of_in_comm_to_keep.add(all_tweets[i])
                else:
                    retweets_of_out_comm_to_keep.add(all_tweets[i])

        print(len(original_tweets_to_keep))
        print(len(retweets_of_in_comm_to_keep))
        print(len(retweets_of_out_comm_to_keep))

        return original_tweets_to_keep, retweets_of_in_comm_to_keep, retweets_of_out_comm_to_keep
    