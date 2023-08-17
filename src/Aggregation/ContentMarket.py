from User.ContentMarketUser import ContentMarketUser
from Tweet.ContentMarketTweet import ContentMarketTweet

from Aggregation.AggregationBase import AggregationBase
from typing import Set, List


def _remove_users(user_id_list: List[int],
                  storage: Set[ContentMarketUser]) -> Set[ContentMarketUser]:
    """Remove all users in <storage> if user_id not in user_id_list.
    """
    removal = set()
    for user in storage:
        if user.user_id not in user_id_list:
            removal.add(user)
    storage.difference_update(removal)
    return removal


def _remove_tweets(user_id_list: List[int],
                   storage: Set[ContentMarketTweet]) -> None:
    """Remove all tweets in <storage> if its user_id not in user_id_list.
    """
    removal = set()
    for tweet in storage:
        if tweet.user_id not in user_id_list:
            removal.add(tweet)
    storage.difference_update(removal)


def _remove_retweets(user_id_list: List[int],
                     storage: Set[ContentMarketTweet]) -> None:
    """Remove all tweets in <storage> if its retweet_user_id not in
    user_id_list."""
    removal = set()
    for tweet in storage:
        if tweet.retweet_user_id not in user_id_list:
            removal.add(tweet)
    storage.difference_update(removal)


class ContentMarket(AggregationBase):
    """
    A class that represents the content market.
    """

    name: str
    consumers: Set[ContentMarketUser]
    producers: Set[ContentMarketUser]
    core_nodes: Set[ContentMarketUser]

    original_tweets: Set[ContentMarketTweet]
    retweets_of_in_comm: Set[ContentMarketTweet]
    retweets_of_out_comm: Set[ContentMarketTweet]
    # add retweets of out community by in community
    retweets_of_out_comm_by_in_comm: Set[ContentMarketTweet]

    def preserve_core_node(self, user_id: int) -> None:
        # get desired user id list
        core_node = self.get_user(user_id)
        follower_list = self._str_to_int_list(core_node.local_followers) # demand
        following_list = self._str_to_int_list(core_node.local_following) # supply

        # remove users
        # 1. remove core nodes
        self.core_nodes.add(core_node)
        other_core_nodes = _remove_users([user_id], self.core_nodes)

        # 2. add to consumer and producer list
        self.consumers.update(other_core_nodes)
        self.producers.update(other_core_nodes)

        # 3. remove from follower and following
        _remove_users(follower_list, self.consumers)
        _remove_users(following_list, self.producers)

        # remove tweets
        _remove_tweets([user_id] + following_list, self.original_tweets)
        _remove_tweets([user_id] + follower_list, self.retweets_of_in_comm)
        _remove_tweets([user_id] + follower_list, self.retweets_of_out_comm)

        # remove retweets
        _remove_retweets([user_id] + following_list, self.retweets_of_in_comm)
        _remove_retweets([user_id] + following_list, self.retweets_of_out_comm)

    def _str_to_int_list(self, lst: List[str]) -> List[int]:
        """Convert a str list to int list."""
        # return [int(s) for s in lst]
        return [self.get_user_id_by_name(name) for name in lst]
