from User.UserBase import UserBase
from Tweet.ContentMarketTweet import ContentMarketTweet

from typing import Set


class ContentMarketUser(UserBase):
    """
    A class that represents a Twitter user that stores ContentMarketTweet
    """
    original_tweets: Set[ContentMarketTweet]
    quotes_of_in_community: Set[ContentMarketTweet]
    quotes_of_out_community: Set[ContentMarketTweet]
    retweets_of_in_community: Set[ContentMarketTweet]
    retweets_of_out_community: Set[ContentMarketTweet]
    replies: Set[ContentMarketTweet]
