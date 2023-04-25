from enum import Enum
from typing import List, Dict, Optional
import datetime


class ContentTweet:
    """
    A class that represents a tweet object
    """

    id: int
    user_id: int
    created_at: datetime
    text: str
    lang: str
    retweet_id: str
    retweet_user_id: str
    quote_id: str
    quote_user_id: str
    # TODO: add hashtags and content_vector here

    def __init__(self, id: int, user_id: int, created_at: datetime, text: str, lang: str,
                 retweet_id: str = None, retweet_user_id: str = None, quote_id: str = None,
                 quote_user_id: str = None):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.text = text
        self.lang = lang
        self.retweet_id = retweet_id
        self.retweet_user_id = retweet_user_id
        self.quote_id = quote_id
        self.quote_user_id = quote_user_id
