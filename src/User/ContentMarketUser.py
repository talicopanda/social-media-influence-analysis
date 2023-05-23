from typing import List, DefaultDict
from collections import defaultdict
from Tweet.ContentMarketTweet import ContentMarketTweet
from Clustering.ContentMarketClustering import ContentMarketClustering


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
        self.original_tweets = kwargs.get("original_tweets", [])
        self.quotes_of_in_community = kwargs.get("quotes_of_in_community", [])
        self.quotes_of_out_community = kwargs.get("quotes_of_out_community", [])
        self.retweets_of_in_community = kwargs.get("retweets_of_in_community", [])
        self.retweets_of_out_community = kwargs.get("retweets_of_out_community", [])

    def build_support(self, tweets: List[ContentMarketTweet], clustering: ContentMarketClustering) -> DefaultDict[tuple, List[ContentMarketTweet]]:
        # TODO: change the type contract
        support = defaultdict(list)
        for tweet in tweets:
            cluster_id = clustering.get_cluster_id(tweet.id)
            support[str(cluster_id)].append(tweet.id)
        return support

    def merge_support(self, support1: DefaultDict[tuple, List[ContentMarketTweet]], support2: DefaultDict[tuple, List[ContentMarketTweet]]):
        for key in support2:
            support1[str(key)].extend(support2[key])

if __name__ == "__main__":
    print(1)
