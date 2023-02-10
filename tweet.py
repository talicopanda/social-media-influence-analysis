from enum import Enum
from typing import List, Dict, Optional
import datetime
import numpy as np


class TweetContent:
    content_str: str  # literal tweet text
    content_vec: List[float]  # semantic vector implementation

    def __init__():
        pass


class TweetType(Enum):
    """
    Possible tweet types
    """
    TWEET = 1
    RETWEET = 2


class Tweet:
    """
    A class that represents a tweet object
    """

    content: TweetContent
    type: TweetType
    user_id: str
    time: datetime

    def __init__(self):
        pass
