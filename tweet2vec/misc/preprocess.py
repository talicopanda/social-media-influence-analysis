import re
import sys
import io
import json
import pymongo
# import emoji
# import nltk
# nltk.download('stopwords')
# from nltk.corpus import stopwords

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


def rachel_preprocess(s, lowercase=True):
    tokens = tokenize(s)
    tokens = [token.lower() for token in tokens]

    # remove emojis
    tokens = [token for token in tokens if not emoji.is_emoji(token)]

    # remove stopwords
    stop_words = stopwords.words('english')
    tokens = [token for token in tokens if token not in stop_words]

    html_regex = re.compile('<[^>]+>')
    tokens = [token for token in tokens if not html_regex.match(token)]

    mention_regex = re.compile('(?:@[\w_]+)')
    # remove usernames entirely
    tokens = [
        '@user' if mention_regex.match(token) else token for token in tokens]
    s = ' '.join([t for t in tokens if t]).replace('rt @user : ', '')
    tokens = tokenize(s)
    tokens = [
        '' if mention_regex.match(token) else token for token in tokens]

    url_regex = re.compile(
        'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+')
    # remove URLs entirely
    tokens = ['' if url_regex.match(token) else token for token in tokens]

    hashtag_regex = re.compile("(?:\#+[\w_]+[\w\'_\-]*[\w_]+)")
    tokens = ['' if hashtag_regex.match(token) else token for token in tokens]

    # remove numbers
    nums_regex = re.compile('[0-9]+')
    tokens = ['' if nums_regex.match(token) else token for token in tokens]

    # remove punctuation
    tokens = ['' if not token.isalnum() else token for token in tokens]

    return ' '.join([t for t in tokens if t])


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

    client = pymongo.MongoClient()

    db_community = client[community_db_name]
    db_content_market = client[content_market_db_name]

    tweets = db_community[tweets_collection_name].find()

    clean_tweets_collection_name = config["database"]["clean_original_tweets_collection"]
    clean_replies_collection_name = config["database"]["clean_replies_collection"]
    for tweet in tweets:
        if tweet["lang"] == "en":
            new_text = preprocess(tweet["text"])

            # Discard tweets that are only urls or user mentions
            # isspace() returns True if all the characters in a string are whitespaces, otherwise False.
            if new_text.replace('!url', '').replace('@user', '').isspace():
                continue

            new_tweet = tweet.copy()
            new_tweet["text"] = new_text

            # separate replies
            if "@user" == new_text[:5]:
                db_content_market[clean_replies_collection_name].insert_one(new_tweet)
            else:
                db_content_market[clean_tweets_collection_name].insert_one(new_tweet)

    collections = [
        # (config["database"]["quotes_of_in_community_collection"], config["database"]["clean_quotes_of_in_community_collection"]),
        # (config["database"]["quotes_of_out_community_collection"], config["database"]["clean_quotes_of_out_community_collection"]),
        (config["database"]["retweets_of_in_community_collection"], config["database"]["clean_retweets_of_in_community_collection"]),
        (config["database"]["retweets_of_out_community_collection"], config["database"]["clean_retweets_of_out_community_collection"]),
        (config["database"]["retweets_of_out_community_by_in_community_collection"], config["database"]["clean_retweets_of_out_community_by_in_community_collection"]),
        ]

    for collec in collections:
        for tweet in db_community[collec[0]].find():
            if tweet["lang"] == "en":
                new_text = preprocess(tweet["text"])

                # Discard tweets that are only urls or user mentions
                # isspace() returns True if all the characters in a string are whitespaces, otherwise False.
                if new_text.replace('!url', '').replace('@user', '').isspace():
                    continue

                new_tweet = tweet.copy()
                new_tweet["text"] = new_text

                db_content_market[collec[1]].insert_one(new_tweet)
