from Mapping.ContentType import ContentType

from Tweet.TweetBase import TweetBase


class ContentSpaceTweet(TweetBase):
    """
    A class that represents a Tweet with ContentType content.
    """
    content: ContentType
