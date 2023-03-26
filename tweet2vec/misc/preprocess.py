import re
import sys
import io
import json

# input and output files
infile = sys.argv[1]
outfile = sys.argv[2]

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


with io.open(infile, 'r') as json_data, io.open(outfile + "_text.txt", 'w') as text_out, io.open(outfile + "_ids.txt", 'w') as ids_out:
    tweets = json.load(json_data)
    for tweet in tweets:
        prep = preprocess(tweet["text"])

        # filter replies
        if "@user" == prep[:5]:
            continue

        # tweets that are only urls or user mentions
        # isspace() returns True if all the characters in a string are whitespaces, otherwise False.
        if prep.replace('!url', '').replace('@user', '').isspace():
            continue

        text_out.write(+ u'\n')
        ids_out.write(str(tweet["id"]) + u'\n')
