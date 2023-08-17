from Tweet.ContentSpaceTweet import ContentSpaceTweet
from DAO.MongoDAOBase import MongoDAOBase
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.TweetType import TweetType
from Mapping.ContentType import ContentType

from typing import Set, List, Dict, Any
from copy import deepcopy

# file global variable
content_space = set()


def _convert_tweet(tweet: ContentSpaceTweet) -> Dict[str, Any]:
    tweet_dict = deepcopy(vars(tweet))
    tweet_dict["content"] = tweet.content.get_representation()
    return tweet_dict


def _serialize_space_tweet(tweets: Set[ContentSpaceTweet]) \
        -> List[Dict[str, Any]]:
    return [_convert_tweet(tweet) for tweet in tweets]


def _populate_content_type(representation: Any,
                           content_type_set: Set[ContentType]) -> ContentType:
    """A helper function returning the ContentType with <representation>.
    If there also exists such ContentType in <content_type_set>, return it;
    else create a new ContentType with <representation>, store in
    <content_type_set>, and return the new one.
    """
    for content_type in content_type_set:
        if content_type.representation == representation:
            # this means that such ContentType has been created,
            # so return the object
            return content_type

    # else create the content type and return the new object
    new_type = ContentType(representation)
    content_type_set.add(new_type)
    return new_type


class ContentSpaceMongoDAO(MongoDAOBase):
    def load_users(self) -> Set[ContentSpaceUser]:
        users = set()
        for user in self.content_space_db[self.content_space_user_info].find():
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
            new_user = ContentSpaceUser(**user_dict)
            users.add(new_user)
        return users

    def _load_tweets(self, db_name: str) -> Set[ContentSpaceTweet]:
        tweets = set()
        for tweet in self.content_space_db[db_name].find():
            del tweet["_id"]
            tweet["text"] = _populate_content_type(tweet["content"],
                                                   content_space)
            tweet.pop("content")
            tweets.add(ContentSpaceTweet(**tweet))
        return tweets

    def load_original_tweets(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(self.content_space_original_tweets_collection)

    def load_quotes_of_in_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_quotes_of_out_community(self) -> Set[ContentSpaceTweet]:
        pass

    def load_retweets_of_in_community(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(self.content_space_retweets_of_in_community_collection)

    def load_retweets_of_out_community(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(self.content_space_retweets_of_out_community_collection)

    # add retweets of out community by in community
    def load_retweets_of_out_community_by_in_community(self) -> Set[ContentSpaceTweet]:
        return self._load_tweets(self.content)

    def load_replies(self) -> Set[ContentSpaceTweet]:
        pass

    def store_users(self, users: Set[ContentSpaceUser]) -> None:
        user_dict_list = []
        for user in users:
            user_dict = deepcopy(vars(user))
            user_dict["original_tweets"] = _serialize_space_tweet(
                user_dict["original_tweets"])
            user_dict["retweets_of_in_community"] = _serialize_space_tweet(
                user_dict["retweets_of_in_community"])
            user_dict["retweets_of_out_community"] = _serialize_space_tweet(
                user_dict["retweets_of_out_community"])
            user_dict["quotes_of_in_community"] = _serialize_space_tweet(
                user_dict["quotes_of_in_community"])
            user_dict["quotes_of_out_community"] = _serialize_space_tweet(
                user_dict["quotes_of_out_community"])
            user_dict["replies"] = _serialize_space_tweet(
                user_dict["replies"])
            user_dict_list.append(user_dict)
        self.content_space_db[self.content_space_user_info].insert_many(
            user_dict_list)

    def store_tweets(self, tweets: Set[ContentSpaceTweet],
                     tweet_type: TweetType) -> None:
        if tweet_type == TweetType.ORIGINAL_TWEET:
            self.content_space_db[self.content_space_original_tweets_collection]\
                .insert_many(_serialize_space_tweet(tweets))
        elif tweet_type == TweetType.RETWEET_OF_IN_COMM:
            self.content_space_db[self.content_space_retweets_of_in_community_collection]\
                .insert_many(_serialize_space_tweet(tweets))
        elif tweet_type == TweetType.RETWEET_OF_OUT_COMM:
            self.content_space_db[
                self.content_space_retweets_of_out_community_collection]\
                .insert_many(_serialize_space_tweet(tweets))
        else:
            raise ValueError

    def store_content_space(self, contents: Set[ContentType]) -> None:
        type_list = [content.get_representation() for content in contents]
        type_dict = [{str(index): type} for index, type in enumerate(type_list)]
        self.content_space_db[self.content_space_collection]\
            .insert_many(type_dict)
