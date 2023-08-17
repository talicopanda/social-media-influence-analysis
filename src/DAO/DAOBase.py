from abc import ABC, abstractmethod

from Tweet.TweetBase import TweetBase
from User.UserBase import UserBase
from Tweet.TweetType import TweetType

from typing import Set, List, Dict


class DAOBase(ABC):
    """
    A parent class for <MongoDAOBase>.
    """
    @abstractmethod
    def load_users(self) -> Set[UserBase]:
        """Load and return a set of users."""
        raise NotImplementedError

    @abstractmethod
    def load_original_tweets(self) -> Set[TweetBase]:
        """Load and return a set of original tweets.
        """
        raise NotImplementedError

    @abstractmethod
    def load_quotes_of_in_community(self) -> Set[TweetBase]:
        """Load and return a set of quotes of in community.
        """
        raise NotImplementedError

    @abstractmethod
    def load_quotes_of_out_community(self) -> Set[TweetBase]:
        """Load and return a set of quotes of out community.
        """
        raise NotImplementedError

    @abstractmethod
    def load_retweets_of_in_community(self) -> Set[TweetBase]:
        """Load and return a set of retweets of in community.
        """
        raise NotImplementedError

    @abstractmethod
    def load_retweets_of_out_community(self) -> Set[TweetBase]:
        """Load and return a set of retweets of out community.
        """
        raise NotImplementedError

    @abstractmethod
    def load_replies(self) -> Set[TweetBase]:
        """Load and return a set of replies.
        """
        raise NotImplementedError

    @abstractmethod
    def load_tweet_embeddings(self) -> Dict[int, List[int]]:
        """Load and return tweet embeddings.
        """
        raise NotImplementedError

    @abstractmethod
    def store_users(self, users: Set[UserBase]) -> None:
        """Store users in database.
        """
        raise NotImplementedError

    @abstractmethod
    def store_tweets(self, tweets: Set[TweetBase],
                     tweet_type: TweetType) -> None:
        """Store tweets in database.
        """
        raise NotImplementedError
