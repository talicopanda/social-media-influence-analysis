"""
TODO:
"""

import pymongo
import json

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

    def get_retweets_of_tweet_id(tweet_id):
        return [tweet for tweet in retweets_in_community_collection.find({"retweet_id": tweet_id})] + [tweet for tweet in retweets_out_community_collection.find({"retweet_id": tweet_id})]

    scores = {user["user_id"]: [0, 0] for user in user_info_collection.find()}

    for user in user_info_collection.find():
        scores[user["user_id"]][1] = user["global_follower_count"]
        for tweet in user["original_tweets"]:
            retweets = get_retweets_of_tweet_id(tweet["id"])
            scores[user["user_id"]][0] += len(retweets)
        
        retweeted_tweets = user["retweets_of_in_community"] + user["retweets_of_out_community"]
        for tweet in retweeted_tweets:
            retweets = get_retweets_of_tweet_id(tweet["id"])
            scores[user["user_id"]][0] += len(retweets) * alpha
        
        print(scores[user["user_id"]])
        
        user_info_collection.update_one({"user_id": user["user_id"]}, 
                                        {"$set": { "social_support": scores[user["user_id"]] }})
    
    return scores
    


if __name__ == "__main__":
    config_file_path = "../config.json"

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()
    
    scores = calculate_social_support("chess_content_space_binning_cleaned", 
                                      config, market=False)
    ranked_ids = list(sorted(scores, key=lambda x: (scores[x][0], scores[x][1]), reverse=True))
    print(ranked_ids[:10])
    core_node_ids = [1330571318971027462, 2233129128, 23612012, 232951413, 3161912605,
                     228806806, 132702118, 1884178352, 1067064666, 313299656]
    print([ranked_ids.index(user_id) for user_id in core_node_ids])

