from Mapping.ContentType import ContentType

import datetime
from typing import Optional, Union


class TweetBase:
    """
    A parent class for <ContentMarketTweet> and <ContentSpaceTweet>.
    """

    id: int
    user_id: Optional[int]
    created_at: datetime
    content: Union[str, ContentType, None]
    lang: Optional[str]
    retweet_id: Optional[str]
    retweet_user_id: Optional[str]
    quote_id: Optional[str]
    quote_user_id: Optional[str]

    def __init__(self, id: int, user_id: int, created_at: datetime,
                 text: Union[str, ContentType], lang: str,
                 retweet_id: str = None, retweet_user_id: str = None,
                 quote_id: str = None, quote_user_id: str = None):
        self.id = id
        self.user_id = user_id
        self.created_at = created_at
        self.content = text
        self.lang = lang
        self.retweet_id = retweet_id
        self.retweet_user_id = retweet_user_id
        self.quote_id = quote_id
        self.quote_user_id = quote_user_id
