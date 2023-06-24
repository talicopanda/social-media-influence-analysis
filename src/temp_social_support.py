"""
TODO:
"""

import pymongo
import json
from tqdm import tqdm

from typing import Dict

def calculate_social_support(db_name: str, config, market: bool, alpha=1.0):
    """<db_name> can correspond to the name of a content market or content space."""

    client = pymongo.MongoClient(config["database"]["connection_url"])
    if market:
        original_tweets_collection = client[db_name][config["database"]["clean_original_tweets_collection"]]
        retweets_in_community_collection = client[db_name][config["database"]["clean_retweets_of_in_community_collection"]]
        retweets_out_community_collection = client[db_name][config["database"]["clean_retweets_of_out_community_collection"]]
        user_info_collection = client[db_name][config["database"]["market_user_info_collection"]]
    else:
        original_tweets_collection = client[db_name][config["database"]["content_space_original_tweets_collection"]]
        retweets_in_community_collection = client[db_name][config["database"]["content_space_retweets_of_in_community_collection"]]
        retweets_out_community_collection = client[db_name][config["database"]["content_space_retweets_of_out_community_collection"]]
        user_info_collection = client[db_name][config["database"]["content_space_user_info"]]

    user_ids = [user["user_id"] for user in user_info_collection.find()]
    # https://github.com/SNACES/core/blob/clustering_trial/src/process/ranking/social_support_ranker.py
    scores = {user_id: [0, 0] for user_id in user_ids}
    ranks = {}
    friends = create_friends_dict(user_ids)
    tweets = [tweet for tweet in original_tweets_collection.find()] + [tweet for tweet in retweets_in_community_collection.find()]
    # Omit self-retweets
    tweets = [tweet for tweet in tweets if tweet["user_id"] != tweet["retweet_user_id"]]
    tweets_by_retweet_group = _group_by_retweet_id(tweets)
    def get_retweets_of_tweet_id(tweet_id):
        return tweets_by_retweet_group.get(str(tweet_id), [])
    def get_later_retweets_of_tweet_id(tweet_id, created_at):
        return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) if tweet["created_at"] > created_at]
    def is_direct_follower(a, b):
        # b follows a
        return a in friends.get(b, [])

    for id in tqdm(user_ids):
        scores[id][1] = user_info_collection.find_one({"user_id": id})["global_follower_count"]
        user_tweets = [tweet for tweet in tweets if tweet["user_id"] == id]
        original_tweet_ids = [tweet["id"] for tweet in user_tweets if tweet["retweet_id"] is None]
        for original_tweet_id in original_tweet_ids:
            retweets = get_retweets_of_tweet_id(original_tweet_id)
            scores[id][0] += len(retweets)

            user_retweets = [tweet for tweet in user_tweets if tweet["retweet_id"] is not None]
            for user_retweet in user_retweets:
                retweets = get_later_retweets_of_tweet_id(user_retweet["retweet_id"], user_retweet["created_at"])
                # The person who retweeted is a direct follower of id.
                retweets_from_direct_followers = [rtw for rtw in retweets if is_direct_follower(id, str(rtw["user_id"]))]
                scores[id][0] += len(retweets_from_direct_followers) * alpha
    
        # print(scores[id])
        ranks[id] = user_info_collection.find_one({"user_id": id})["rank"]
    
        user_info_collection.update_one({"user_id": id}, 
                                        {"$set": { "social_support": scores[id] }})
            
    
    return scores, ranks


def create_friends_dict(user_ids):
    friends = {}
    client = pymongo.MongoClient("mongodb://localhost:27017/")
    community_info_collection = client["chess_community"]["community_info"]
    for user_id in user_ids:
        friends_of_user_id = community_info_collection.find_one({"userid": user_id})["local following list"]
        friends[user_id] = [str(id) for id in friends_of_user_id]
    return friends


def _group_by_retweet_id(tweets) -> Dict:
    # Puts all tweets with the same retweet_id in the same list
    # Returns: A dictionary where the key is the retweet_id and
    # the value is the list of tweets with that retweet_id
    dict = {}
    for tweet in tweets:
        key = str(tweet["retweet_id"])
        if key in dict:
            dict[key].append(tweet)
        else:
            dict[key] = [tweet]

    return dict



if __name__ == "__main__":
    config_file_path = "../config.json"

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()
    
    scores, ranks = calculate_social_support("rachel_chess_content_space_binning", 
                                      config, market=False)
    ranked_ids = list(sorted(scores, key=lambda x: (scores[x][0], scores[x][1]), reverse=True))
    print(ranked_ids[:10])
    print([scores[ranked_id] for ranked_id in ranked_ids][:10])
    print([ranks[ranked_id] for ranked_id in ranked_ids][:10])
    core_node_ids = [1330571318971027462, 2233129128, 23612012, 232951413, 3161912605,
                     228806806, 132702118, 1884178352, 1067064666, 313299656]
    print([ranked_ids.index(user_id) for user_id in core_node_ids])

    print("Original rank: " + str(sorted(ranks, key=lambda user_id: ranks[user_id])))
    print("Social support rank: " + str(ranked_ids))

