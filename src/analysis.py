from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder 
from UserPartitioning import UserPartitioningStrategyFactory
from DAO.DAOFactory import DAOFactory
from User.UserType import UserType

from typing import Dict, List
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Collection, Dict, Any
import random
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
import math
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from scipy import integrate
from scipy.stats import gaussian_kde, rv_histogram, relfreq
from datetime import datetime
from dateutil import rrule


### Plotting Functions #############################################################################
def plot_demand_and_supply(ds, demand_in_community_keys: Collection[str], supply_keys: Collection[str]):
    """Plot the demand and supply curves for the binning embedding."""
    # print(ds.demand_in_community.keys())
    for key in demand_in_community_keys:
        print(sorted(ds.demand_in_community[key].keys()))
        plt.bar(sorted(ds.demand_in_community[key].keys()), 
                [len(ds.demand_in_community[key][content_type]) for content_type in sorted(ds.demand_in_community[key].keys())],
                alpha=0.3, label=key.value)
    
    for key in supply_keys:
        print(ds.supply[key].keys())
        plt.bar(sorted(ds.supply[key].keys()), 
                [len(ds.supply[key][content_type]) for content_type in sorted(ds.supply[key].keys())],
                alpha=0.3, label=key.value)
    plt.legend()
    plt.show()


def plot_bin_distances(market, space):
    term_to_weights = relative_frequency(market, space)
    heatmap = []
    for i in range(20):
        row = []
        for j in range(20):
            row.append(10 - len(set(term_to_weights[i]).intersection(term_to_weights[j])))
        heatmap.append(row)
    sns.heatmap(heatmap)
    plt.show()

### Bin Analysis ###################################################################################
def bin_interpretations(market, space, content_type: int, num_comments: int):
    """Print a random sample of <num_comments> comments from the database that have content type 
    <content_type>."""
    np.random.seed(42)
    all_tweets = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
    print(len(all_tweets))
    content_type_tweets = []
    for space_tweet in all_tweets:
        # print(space_tweet.content)
        if space_tweet.content.representation == content_type:
            market_tweet = market.get_tweet(space_tweet.id)
            content_type_tweets.append(market_tweet)
    print("Number of tweets in bin " + str(content_type) + ": " + str(len(content_type_tweets)))
    samples = np.random.choice(content_type_tweets, min(len(content_type_tweets), num_comments), 
                               replace=False)
    for market_tweet in samples:
        print(market_tweet.content)


def number_of_tweets_in_bin(market, space, content_type):
    all_tweets = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
    count = 0
    for space_tweet in all_tweets:
        if space_tweet.content.representation == content_type:
            count += 1
    return count


### TF*PDF Analysis - Channel = Bin ################################################################
def tf_pdf_weights(market, space, channel):
    """<channel> is a bin number in the binning algorithm."""
    corpus = initialize_channel_corpus(market, space, channel)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    X = X.todense()
    term_list = vectorizer.get_feature_names_out()

    term_to_weight = {}

    for term_idx in range(len(term_list)):
        F = tf_pdf_frequency(X, term_idx)
        n = np.count_nonzero(X[:, term_idx])
        N = len(corpus)
        term_to_weight[term_list[term_idx]] = F * np.exp(n / N)

    return term_to_weight


def tf_pdf_frequency(X, term_idx):
    """<X> is a 2D list, representing the output from the CountVectorizer.
    <term_idx> is the index of the term in <X>."""
    numerator = X[:, term_idx].sum()
    denominator = tf_pdf_frequency_denom(X)
    return numerator / denominator

def tf_pdf_frequency_denom(X):
    """<X> is a 2D list, representing the output from the CountVectorizer."""
    term_freqs = X.sum(axis=0)
    term_freqs_squared = np.square(term_freqs)
    return math.sqrt(term_freqs_squared.sum())


def initialize_channel_corpus(market, space, channel):
    """Initialize the corpus for a given channel.
    <market> is a content market. <channel> is a bin number in the binning algorithm.
    The corpus is a list of all the tweets, where each tweet is a string.
    Assume that the preprocessing of the tweets has already been done (i.e. removing numbers and 
    punctuation, stopwords, etc.)"""
    all_tweets = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
    corpus = []
    for space_tweet in all_tweets:
        if space_tweet.content.representation == channel:
            market_tweet = market.get_tweet(space_tweet.id)
            corpus.append(market_tweet.content)

            # Rachel
            # corpus.append(preprocess(market_tweet.content))
    return corpus


def initialize_market_corpus(market, space):
    corpus = []
    for i in range(20):
        corpus.extend(initialize_channel_corpus(market, space, i))
    return corpus


### Relative Frequency - Words #####################################################################
def relative_frequency(market, space):
    corpus = initialize_market_corpus(market, space)
    vectorizer = CountVectorizer(min_df=0.01)
    X = vectorizer.fit_transform(corpus)
    X = X.todense()
    X = np.array(X)

    term_freqs = np.count_nonzero(X, axis=0)  # X.sum(axis=0)
    term_list = vectorizer.get_feature_names_out()
    print(len(term_list))

    bin_counts = []
    for i in range(20):
        bin_counts.append(number_of_tweets_in_bin(market, space, i))
    bin_boundaries = [0]
    sum_so_far = 0
    for i in range(20):
        sum_so_far += bin_counts[i]
        bin_boundaries.append(sum_so_far)

    term_to_weights = []
    for i in range(20):
        term_to_weight = {}
        term_freqs_in_channel = np.count_nonzero(X[bin_boundaries[i]:bin_boundaries[i + 1]], axis=0)  # X[bin_boundaries[i]:bin_boundaries[i + 1]].sum(axis=0)
        rel_freqs = term_freqs_in_channel / term_freqs
        for j in range(len(term_list)):
            term_to_weight[term_list[j]] = rel_freqs[j]
        term_to_weights.append(sorted(term_to_weight, key=lambda term: term_to_weight[term], reverse=True)[:10])
        print(sorted(term_to_weight, key=lambda term: term_to_weight[term], reverse=True)[:10])
    
    return term_to_weights


### Relative Frequency - Hashtags ##################################################################
def relative_frequency_hashtags(market, space, tweet_to_hashtags: Dict[int, List[str]]):
    corpus = initialize_hashtag_corpus(market, space, tweet_to_hashtags)
    vectorizer = CountVectorizer(min_df=0.01)
    X = vectorizer.fit_transform(corpus)
    X = X.todense()
    X = np.array(X)
    term_freqs = np.count_nonzero(X, axis=0)  # X.sum(axis=0)
    term_list = vectorizer.get_feature_names_out()
    print(len(term_list))

    bin_counts = []
    for i in range(20):
        bin_counts.append(number_of_tweets_in_bin(market, space, i))
    bin_boundaries = [0]
    sum_so_far = 0
    for i in range(20):
        sum_so_far += bin_counts[i]
        bin_boundaries.append(sum_so_far)

    for i in range(20):
        term_to_weight = {}
        term_freqs_in_channel = np.count_nonzero(X[bin_boundaries[i]:bin_boundaries[i + 1]], axis=0)  # X[bin_boundaries[i]:bin_boundaries[i + 1]].sum(axis=0)
        rel_freqs = term_freqs_in_channel / term_freqs
        for j in range(len(term_list)):
            term_to_weight[term_list[j]] = rel_freqs[j]
        print(sorted(term_to_weight, key=lambda term: term_to_weight[term], reverse=True)[:10])


def initialize_channel_hashtag_corpus(market, space, tweet_to_hashtags: Dict[int, List[str]], channel):
    """Initialize the corpus for a given channel.
    <market> is a content market. <channel> is a bin number in the binning algorithm.
    The corpus is a list of all the tweets, where each tweet is a string.
    Assume that the preprocessing of the tweets has already been done (i.e. removing numbers and 
    punctuation, stopwords, etc.)"""
    all_tweets = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
    corpus = []
    for space_tweet in all_tweets:
        if space_tweet.content.representation == channel:
            hashtags = tweet_to_hashtags[space_tweet.id]
            corpus.append(" ".join(hashtags))

            # Rachel
            # corpus.append(preprocess(market_tweet.content))
    return corpus


def initialize_hashtag_corpus(market, space, tweet_to_hashtags: Dict[int, List[str]]):
    corpus = []
    for i in range(20):
        corpus.extend(initialize_channel_hashtag_corpus(market, space, tweet_to_hashtags, i))
    return corpus


### Bhattacharyya Distances ########################################################################
def bhattacharyya_distance(dict1, dict2):
    """Calculate the Bhattacharyya distance. 
    <dict1>, <dict2> are dictionaries that map each content type to a set of tweets."""

    # with histogram:
    a = convert_to_relative_frequencies(dict1)
    b = convert_to_relative_frequencies(dict2)
    

    bhattacharyya_coefficient = 0
    for i in range(5):
        if a[i] == 0 or b[i] == 0:
            bhattacharyya_coefficient += 0
        else:
            bhattacharyya_coefficient \
                += np.sqrt(a[i] * b[i])

    print(bhattacharyya_coefficient)

    return -np.log(bhattacharyya_coefficient)


def plot_bhattacharyya_distances(ds, sorted_user_ids):
    """Calculate the Bhattacharyya distance between each user's curve and the aggregate demand."""
    # user_id_to_production_utility = get_user_id_to_social_support(db_config)
    # sorted_user_ids = sorted(user_id_to_production_utility, 
    #                          key=lambda user_id: user_id_to_production_utility[user_id],
    #                          reverse=True)
    
    dict1 = pad_dictionary(ds.demand_in_community[UserType.CONSUMER]) 
    dict2 = pad_dictionary(ds.demand_in_community[UserType.CORE_NODE])
    for content_type in range(20):
        dict1[content_type] = dict1[content_type].union(dict2[content_type])
    
    curr_rank = 1
    ranks = []
    bhattacharyya_distances = []
    for user_id in sorted_user_ids:
        print(curr_rank)
        dict2 = pad_dictionary(ds.supply[str(user_id)])
        ranks.append(curr_rank)
        bhattacharyya_distances.append(bhattacharyya_distance(dict1, dict2))
        curr_rank += 1

    print(np.corrcoef(ranks, bhattacharyya_distances))
    plt.plot(ranks, bhattacharyya_distances)
    plt.xlabel("Regular Rank")
    plt.ylabel("Bhattacharyya Distance with All In Community Demand")
    plt.show()


def convert_to_relative_frequencies(d) -> Dict[Any, float]:
    """d is a dictionary that maps each content type to a set of tweets."""
    total = sum(len(d[content_type]) for content_type in d)
    content_type_to_relative_frequency = {}
    for content_type in d:
        content_type_to_relative_frequency[content_type] = len(d[content_type]) / total
    return content_type_to_relative_frequency


def pad_dictionary(d):
    """d is a dictionary that maps each content type to a set of tweets.
    For content types that are not in the dictionary, add a key corresponding to the content type 
    and an empty set."""
    padded_dict = {}
    for content_type in range(20):
        if content_type in d:
            padded_dict[content_type] = d[content_type]
        else:
            padded_dict[content_type] = set()
    return padded_dict


if __name__ == "__main__":
    # retrieve configuration
    config_file_path = "../config.json"

    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()

    dao_factory = DAOFactory()
    partition = UserPartitioningStrategyFactory.get_user_type_strategy(
    config["partitioning_strategy"])

    market_dao = dao_factory.get_content_market_dao(config["database"])
    market_builder = ContentMarketBuilder(config["database"]["content_market_db_name"],
                                          market_dao, partition)
    market = market_builder.load()
    
    space_dao = dao_factory.get_content_space_dao(config["database"])
    space_builder = ContentSpaceBuilder(
        config["database"]["content_space_db_name"],
        space_dao, partition)
    space = space_builder.load()

    ds_dao = dao_factory.get_supply_demand_dao(config["database"])
    ds_builder = ContentDemandSupplyBuilder(
            config["database"]["content_demand_supply_db_name"], ds_dao)
    ds = ds_builder.load()

    plot_demand_and_supply(ds, [UserType.CONSUMER, UserType.CORE_NODE], [UserType.PRODUCER, UserType.CORE_NODE])
    
    # for i in range(20):
    #     bin_interpretations(market, space, i, 10)
    #     print()

    # for i in range(20):
    #     term_to_weight = tf_pdf_weights(market, i)
    #     print(i)
    #     print(sorted(term_to_weight, key=lambda term: term_to_weight[term], reverse=True)[:10])
    #     print()

    # tf_idf(market)

    # relative_frequency(market, space)

    # tweet_to_hashtags = market_dao.load_hashtags()
    # relative_frequency_hashtags(market, space, tweet_to_hashtags)

    # plot_bin_distances(market, space)

    # users = ds.producers.union(ds.core_nodes.union(ds.consumers))
    plot_bhattacharyya_distances(ds, 
                                 [1330571318971027462, 2233129128, 23612012, 232951413, 3161912605, 228806806, 132702118, 1884178352, 1067064666, 313299656, 277594186, 917892794953404417, 94340676, 3392260661, 60494861, 919900711, 126345156, 228660231, 186797066, 301042394, 83338597, 609121227, 1651411087, 28994084, 1081889952412119040, 1729528081, 4369711156, 161308987, 1495255914, 1167467303002345474, 29521967, 499173831, 1356595452, 1093199136596287489, 3511819222, 297267701, 13247182, 1702864658, 425376095, 77210396, 75174049, 1041446451715473408, 46465628, 617004214, 92284830, 4922808130, 391563229, 406172437, 31479252, 217741900, 480444935, 227629567, 1588889406, 97426170, 354486695, 101850896, 1110733580, 3086225424, 434270813, 2609917590, 277634312, 167842102, 132787956, 953260427475079168, 252909412, 898166654575751172, 247232127, 337149339, 198339335, 71476598, 769229557576507392, 279565150, 22202577, 19647809, 60995997, 185677963])