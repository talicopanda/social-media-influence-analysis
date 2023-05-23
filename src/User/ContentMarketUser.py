from Tweet.ContentMarketTweet import ContentMarketTweet
from Clustering.ContentMarketClustering import ContentMarketClustering

from typing import List, DefaultDict, Any, Set
from collections import defaultdict


class ContentMarketUser:
    """
    A class that represents a Twitter user in a content market
    """

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

    """
    A class that represents a twitter user in a content market
    """

    def __init__(self, **kwargs):
        self.user_id = int(kwargs.get("user_id"))
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
        self.original_tweets = set(kwargs.get("original_tweets", []))
        self.quotes_of_in_community = set(kwargs.get("quotes_of_in_community", []))
        self.quotes_of_out_community = set(kwargs.get("quotes_of_out_community", []))
        self.retweets_of_in_community = set(kwargs.get("retweets_of_in_community", []))
        self.retweets_of_out_community =set(kwargs.get("retweets_of_out_community", []))

    def build_support(self, tweets: Set[ContentMarketTweet],
                      clustering: ContentMarketClustering) \
            -> DefaultDict[Any, Set[ContentMarketTweet]]:
        # Use the representation of ContentType as key to the output dict
        support = defaultdict(set)
        for tweet in tweets:
            tweet_id = int(tweet.id)
            content_type = clustering.get_content_type(tweet_id)
            support[content_type.get_representation()].add(tweet)
        return support

    def merge_support(self, support1: DefaultDict[Any, Set[ContentMarketTweet]], support2: DefaultDict[Any, Set[ContentMarketTweet]]):
        for key in support2:
            support1[key].update(support2[key])
