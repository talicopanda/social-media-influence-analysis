import re
import sys
import io
import json
import pymongo

db_config = sys.argv[1]

regex_str = [
    r'<[^>]+>',  # HTML tags
    r'(?:@[\w_]+)',  # @-mentions
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)",  # hash-tags
    # URLs
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+',

    r'(?:(?:\d+,?)+(?:\.?\d+)?)',  # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])",  # words with - and '
    r'(?:[\w_]+)',  # other words
    r'(?:\S)+'  # anything else
]

tokens_re = re.compile(r'('+'|'.join(regex_str)+')',
                       re.VERBOSE | re.IGNORECASE)


def tokenize(s):
    return tokens_re.findall(s)


def preprocess(s, lowercase=True):
    tokens = tokenize(s)
    tokens = [token.lower() for token in tokens]

    html_regex = re.compile('<[^>]+>')
    tokens = [token for token in tokens if not html_regex.match(token)]

    mention_regex = re.compile('(?:@[\w_]+)')
    tokens = [
        '@user' if mention_regex.match(token) else token for token in tokens]

    url_regex = re.compile(
        'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+')
    tokens = ['!url' if url_regex.match(token) else token for token in tokens]

    hashtag_regex = re.compile("(?:\#+[\w_]+[\w\'_\-]*[\w_]+)")
    tokens = ['' if hashtag_regex.match(token) else token for token in tokens]

    return ' '.join([t for t in tokens if t]).replace('rt @user : ', '')


with io.open(db_config, 'r') as config_file:
    config = json.load(config_file)

    community_db_name = config["database"]["community_db_name"]
    content_market_db_name = config["database"]["content_market_db_name"]
    
    tweets_collection_name = config["database"]["original_tweets_collection"]

    clean_tweets_collection_name = config["database"]["clean_original_tweets_collection"]
    clean_replies_collection_name = config["database"]["clean_replies_collection"]

    client = pymongo.MongoClient()

    db_community = client[community_db_name]
    db_content_market = client[content_market_db_name]

    tweets = db_community[tweets_collection_name].find()

    clean_tweets = []
    clean_replies = []
    for tweet in tweets:
        new_text = preprocess(tweet["text"])

        # Discard tweets that are only urls or user mentions
        # isspace() returns True if all the characters in a string are whitespaces, otherwise False.
        if new_text.replace('!url', '').replace('@user', '').isspace():
            continue

        new_tweet = tweet.copy()
        new_tweet["text"] = new_text

        # separate replies
        if "@user" == new_text[:5]:
            clean_replies.append(new_tweet)
        else:
            clean_tweets.append(new_tweet)

    db_content_market[clean_tweets_collection_name].insert_many(clean_tweets)
    db_content_market[clean_replies_collection_name].insert_many(clean_replies)