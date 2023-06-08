from User.UserBase import UserBase
from Tweet.ContentSpaceTweet import ContentSpaceTweet

from typing import Set


class ContentSpaceUser(UserBase):
    """
    A class that represents a Twitter user that stores ContentSpaceTweet
    """
    original_tweets: Set[ContentSpaceTweet]
    quotes_of_in_community: Set[ContentSpaceTweet]
    quotes_of_out_community: Set[ContentSpaceTweet]
    retweets_of_in_community: Set[ContentSpaceTweet]
    retweets_of_out_community: Set[ContentSpaceTweet]
    replies: Set[ContentSpaceTweet]
