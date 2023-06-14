from Tweet.TweetBase import TweetBase

import datetime


class MinimalTweet(TweetBase):
    """
    A Tweet contains minimal information for supply and demand generation
    """

    id: int
    created_at: datetime

    def __init__(self, id: int, created_at: datetime):
        super().__init__(id, None, created_at, None, None, None, None, None, None)
