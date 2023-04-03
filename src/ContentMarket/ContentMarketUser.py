from typing import List
from ContentMarket.ContentTweet import ContentTweet

class ContentMarketUser:
    user_id: int
    rank: int
    username: str
    influence_one: float
    influence_two: float
    production_utility: float
    consumption_utility: float
    local_follower_count: int
    local_following_count: int
    local_followers: List[int]
    local_following: List[int]
    global_follower_count: int
    global_following_count: int 
    is_new_user: bool
    original_tweets: List[ContentTweet]
    quotes_of_in_community: List[ContentTweet]
    quotes_of_out_community: List[ContentTweet]
    retweets_of_in_commuinity: List[ContentTweet]
    retweets_of_out_commuinity: List[ContentTweet]
    
    """
    A class that represents a twitter user in a content market
    """

    def __init__(self, **kwargs):
        self.user_id = kwargs.get("user_id")
        self.rank = kwargs.get("rank")
        self.username = kwargs.get("username")
        self.influence_one = kwargs.get("influence_one")
        self.influence_two = kwargs.get("influence_two")
        self.production_utility = kwargs.get("production_utility")
        self.consumption_utility = kwargs.get("consumption_utility")
        self.local_follower_count = kwargs.get("local_follower_count")
        self.local_following_count = kwargs.get("local_following_count")
        self.local_followers = kwargs.get("local_followers")
        self.local_following = kwargs.get("local_following")
        self.global_follower_count = kwargs.get("global_follower_count")
        self.global_following_count = kwargs.get("global_following_count")
        self.is_new_user = kwargs.get("is_new_user")
        self.original_tweets = []
        self.quotes_of_in_community = []
        self.quotes_of_out_community = []
        self.retweets_of_in_community = []
        self.retweets_of_out_community = []
