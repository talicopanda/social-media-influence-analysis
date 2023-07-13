from DAO.MongoDAOBase import MongoDAOBase
from Tweet.ContentMarketTweet import ContentMarketTweet
from User.ContentMarketUser import ContentMarketUser
from Tweet.TweetType import TweetType

from typing import Dict, Any, Set, List


def _serialize_market_tweet(tweets: Set[ContentMarketTweet]) \
        -> List[Dict[str, Any]]:
    return [vars(tweet) for tweet in tweets]


class ContentMarketMongoDAO(MongoDAOBase):
    def load_users(self) -> Set[ContentMarketUser]:
        users = set()
        for user in self.content_market_db[self.market_user_info_collection].find():
            user_dict = {
                "user_id": user["user_id"],
                "rank": user["rank"],
                "username": user["username"],
                "influence_one": user["influence_one"],
                "influence_two": user["influence_two"],
                "production_utility": user["production_utility"],
                "consumption_utility": user["consumption_utility"],
                "local_follower_count": user["local_follower_count"],
                "local_following_count": user["local_following_count"],
                "local_followers": user["local_followers"],
                "local_following": user["local_following"],
                "global_follower_count": user["global_follower_count"],
                "global_following_count": user["global_following_count"],
                "is_new_user": user["is_new_user"]
            }
            new_user = ContentMarketUser(**user_dict)
            users.add(new_user)
        return users

    def create_users(self) -> Set[ContentMarketUser]:
        users = set()
        for user in self.community_db[self.community_info_collection].find():
            user_dict = {
                "user_id": user["userid"],
                "rank": user["rank"],
                "username": user["username"],
                "influence_one": user["influence one"],
                "influence_two": user["influence two"],
                # "production_utility": user["production utility"],
                # "consumption_utility": user["consumption utility"],
                "local_follower_count": user["local follower"],
                "local_following_count": user["local following"],
                "local_followers": user["local follower list"],
                "local_following": user["local following list"],
                "global_follower_count": user["global follower"],
                "global_following_count": user["global following"],
                # "is_new_user": user["is new user"]
            }
            new_user = ContentMarketUser(**user_dict)
            users.add(new_user)
        return users

    def _load_tweets(self, db_name: str) -> Set[ContentMarketTweet]:
        tweets = set()
        for tweet in self.content_market_db[db_name].find():
            del tweet["_id"]
            tweet["id"] = int(tweet["id"])
            tweet["user_id"] = int(tweet["user_id"])
            tweets.add(ContentMarketTweet(**tweet))
        return tweets

    def load_original_tweets(self) -> Set[ContentMarketTweet]:
        return self._load_tweets(self.clean_original_tweets_collection)

    def load_quotes_of_in_community(self) -> Set[ContentMarketTweet]:
        return self._load_tweets(self.clean_quotes_of_in_community_collection)

    def load_quotes_of_out_community(self) -> Set[ContentMarketTweet]:
        return self._load_tweets(self.clean_quotes_of_out_community_collection)

    def load_retweets_of_in_community(self) -> Set[ContentMarketTweet]:
        return self._load_tweets(self.clean_retweets_of_in_community_collection)

    def load_retweets_of_out_community(self) -> Set[ContentMarketTweet]:
        return self._load_tweets(self.clean_retweets_of_out_community_collection)

    def load_replies(self) -> Set[ContentMarketTweet]:
        return self._load_tweets(self.clean_replies_collection)

    def store_users(self, users: Set[ContentMarketUser]) -> None:
        user_dict_list = []
        for user in users:
            user_dict = vars(user)
            user_dict["original_tweets"] = _serialize_market_tweet(
                user_dict["original_tweets"])
            user_dict["retweets_of_in_community"] = _serialize_market_tweet(
                user_dict["retweets_of_in_community"])
            user_dict["retweets_of_out_community"] = _serialize_market_tweet(
                user_dict["retweets_of_out_community"])
            user_dict["quotes_of_in_community"] = _serialize_market_tweet(
                user_dict["quotes_of_in_community"])
            user_dict["quotes_of_out_community"] = _serialize_market_tweet(
                user_dict["quotes_of_out_community"])
            user_dict["replies"] = _serialize_market_tweet(
                user_dict["replies"])
            user_dict_list.append(user_dict)
        self.content_market_db[self.market_user_info_collection].insert_many(
            user_dict_list)

    def store_tweets(self, tweets: Set[ContentMarketTweet],
                     tweet_type: TweetType) -> None:
        pass
