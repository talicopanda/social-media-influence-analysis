"""
Because generating the embeddings takes so long, this is a temporary module that takes the existing
embeddings in the content market (that were created by encode_char_from_db.py), and makes sure that
the supply and the demand align.
"""

import pymongo
import json

def old_to_new_embeddings(config):
    client = pymongo.MongoClient(config["database"]["connection_url"])
    content_market_db_name = config["database"]["content_market_db_name"]
    original_tweets_collection = client[content_market_db_name][config["database"]["clean_original_tweets_collection"]]
    retweets_in_community_collection = client[content_market_db_name][config["database"]["clean_retweets_of_in_community_collection"]]
    retweets_out_community_collection = client[content_market_db_name][config["database"]["clean_retweets_of_out_community_collection"]]
    old_embeddings_collection = client[content_market_db_name][config["database"]["tweet_embeddings_collection"]]

    hashtags, embeddings = {}, {}
    i = 0
    print(original_tweets_collection.find())
    for tweet in original_tweets_collection.find():
        if i % 1000 == 0:
            print(i)
        i += 1
        hashtags[tweet["id"]] = \
            old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
        embeddings[tweet["id"]] = \
            old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["embedding"]
    for tweet in retweets_in_community_collection.find():
        if i % 1000 == 0:
            print(i)
        i += 1
        if tweet["retweet_id"] in embeddings:
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["retweet_id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["retweet_id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["embedding"]
        else:
            # if the parent is not in the embedding, embed the comment directly into the space
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["embedding"]
    for tweet in retweets_out_community_collection.find():
        if i % 1000 == 0:
            print(i)
        i += 1
        if tweet["retweet_id"] in embeddings:
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["retweet_id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["retweet_id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["embedding"]
        else:
            # if the parent is not in the embedding, embed the comment directly into the space
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["embedding"]
    
    print(len(embeddings))

    i = 0
    for tweet_id in embeddings:
        if i % 1000 == 0:
            print(i)
        i += 1
        client[content_market_db_name]["tweet_embeddings_supply_only"].insert_one({"id": tweet_id, "hashtags": hashtags[tweet_id], "embedding": embeddings[tweet_id]})
    
    return embeddings


def remove_non_english_embeddings(config):
    client = pymongo.MongoClient(config["database"]["connection_url"])
    content_market_db_name = config["database"]["content_market_db_name"]
    original_tweets_collection = client[content_market_db_name][config["database"]["clean_original_tweets_collection"]]
    retweets_in_community_collection = client[content_market_db_name][config["database"]["clean_retweets_of_in_community_collection"]]
    retweets_out_community_collection = client[content_market_db_name][config["database"]["clean_retweets_of_out_community_collection"]]
    old_embeddings_collection = client[content_market_db_name][config["database"]["tweet_embeddings_collection"]]

    non_english_ids = set()
    hashtags, embeddings = {}, {}
    i = 0
    for tweet in original_tweets_collection.find():
        if tweet["lang"] != "en":
            non_english_ids.add(tweet["id"])
    for tweet in retweets_in_community_collection.find():
        if tweet["lang"] != "en":
            non_english_ids.add(tweet["id"])
    for tweet in retweets_out_community_collection.find():
        if tweet["lang"] != "en":
            non_english_ids.add(tweet["id"])

    for tweet in original_tweets_collection.find():
        if i % 1000 == 0:
            print(i)
        i += 1
        if tweet["id"] not in non_english_ids:
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "embedding": 1, "_id": 0 })["embedding"]
    for tweet in retweets_in_community_collection.find():
        if i % 1000 == 0:
            print(i)
        i += 1
        if tweet["id"] not in non_english_ids:
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "embedding": 1, "_id": 0 })["embedding"]
    for tweet in retweets_out_community_collection.find():
        if i % 1000 == 0:
            print(i)
        i += 1
        if tweet["id"] not in non_english_ids:
            hashtags[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "hashtags": 1, "embedding": 1, "_id": 0 })["hashtags"]
            embeddings[tweet["id"]] = \
                old_embeddings_collection.find_one({ "id": tweet["id"] }, { "embedding": 1, "_id": 0 })["embedding"]
    
    print(len(embeddings))

    i = 0
    for tweet_id in embeddings:
        if i % 1000 == 0:
            print(i)
        i += 1
        client[content_market_db_name]["tweet_embeddings_english_only"].insert_one({"id": tweet_id, "hashtags": hashtags[tweet_id], "embedding": embeddings[tweet_id]})
    
    return embeddings

if __name__ == "__main__":
    config_file_path = "../config.json"

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()
    # embeddings = old_to_new_embeddings(config)
    embeddings = remove_non_english_embeddings(config)
    print(len(embeddings))