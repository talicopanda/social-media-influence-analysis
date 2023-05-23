from enum import Enum
from typing import List
import datetime
import numpy as np


class tempTweet:
    """
    A class that represents a tweet object
    """

    user_id: int
    id: int
    hashtags: List[str]
    text: str
    timestamp: datetime

    def __init__(self, user_id, id, hashtags, text, timestamp):
        self.user_id = user_id
        self.id = id
        self.hashtags = hashtags
        self.text = text
        self.timestamp = timestamp
