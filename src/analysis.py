from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder 
from UserPartitioning import UserPartitioningStrategyFactory
from DAO.DAOFactory import DAOFactory
from User.UserType import UserType
from TS.TimeSeriesBuilder import TimeSeriesBuilder
from Tweet.MinimalTweet import MinimalTweet

from typing import Dict, List, Union
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
from datetime import datetime, timedelta
from dateutil import rrule
from tqdm import tqdm


### Plotting Functions #############################################################################
def plot_demand_and_supply(ds, demand_in_community_keys: Collection[Union[UserType, int]], 
                           supply_keys: Collection[Union[UserType, int]]):
    """Plot the demand and supply curves for the binning embedding."""
    # print(ds.demand_in_community.keys())
    for key in demand_in_community_keys:
        print(sorted(ds.demand_in_community[key].keys()))
        plt.bar(sorted(ds.demand_in_community[key].keys()), 
                [len(ds.demand_in_community[key][content_type]) 
                 for content_type in sorted(ds.demand_in_community[key].keys())],
                alpha=0.3, label=key.value)
    
    for key in supply_keys:
        print(ds.supply[key].keys())
        plt.bar(sorted(ds.supply[key].keys()), 
                [len(ds.supply[key][content_type]) 
                 for content_type in sorted(ds.supply[key].keys())],
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


def plot_bhattacharyya_distances(ds, sorted_user_ids):
    """Calculate the Bhattacharyya distance between each user's curve and the aggregate demand."""   
    dict1 = pad_dictionary(ds.demand_in_community[UserType.CONSUMER]) 
    dict2 = pad_dictionary(ds.demand_in_community[UserType.CORE_NODE])
    for content_type in range(20):
        dict1[content_type] = dict1[content_type].union(dict2[content_type])
    
    curr_rank = 0
    ranks = []
    bhattacharyya_distances = []
    for user_id in sorted_user_ids:
        if len(ds.supply[user_id]) != 0:
            dict2 = pad_dictionary(ds.supply[user_id])
            ranks.append(curr_rank)
            bhattacharyya_distances.append(bhattacharyya_distance(dict1, dict2))
            curr_rank += 1

    print(np.corrcoef(ranks, bhattacharyya_distances))
    plt.plot(ranks, bhattacharyya_distances)
    plt.xlabel("Social Support Rank")
    plt.ylabel("Bhattacharyya Distance with All In Community Demand")
    plt.show()


def plot_bhattacharyya_and_social_support_rank(space, ds, ts_builder, user_id: int):
    supply_list = ts_builder.create_mapping_series("supply")
    demand_in_community_list = ts_builder.create_mapping_series("demand_in_community")
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    retweets_of_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")

    bhattacharyya_ranks, social_support_ranks = [], []
    bhattacharyya_time_stamps, social_support_time_stamps = [], [] 
    for i in range(len(supply_list)):
        bhattacharyya_rank \
            = calculate_bhattacharyya_ranks(space, ds, supply_list[i], demand_in_community_list[i])[user_id]
        social_support_rank \
            = calculate_social_support_ranks(space, original_tweets_list[i], retweets_of_in_comm_list[i])[user_id]
        bhattacharyya_ranks.append(bhattacharyya_rank)
        social_support_ranks.append(social_support_rank)
    plt.figure(figsize=(10, 5))
    print(ts_builder.time_stamps)
    plt.plot(ts_builder.time_stamps, bhattacharyya_ranks, label="Bhattacharyya Rank")
    plt.plot(ts_builder.time_stamps, social_support_ranks, label="Social Support Rank")
    plt.legend()
    plt.ylabel("Rank")
    plt.title("user_id: " + str(user_id))
    plt.show()
    plt.savefig("../results/bhattacharyya_and_social_support_" + str(user_id))


def plot_social_support_for_top_bhattacharyya(space, ds):
    bhattacharyya = calculate_bhattacharyya_ranks(space, ds, ds.supply, ds.demand_in_community)
    top_bhattacharyya = sorted(bhattacharyya, key=lambda x: bhattacharyya[x], reverse=False)[:10]
    print(top_bhattacharyya)
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    retweets_of_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")
    to_plot = []
    for user_id in top_bhattacharyya:
        social_support_ranks = []
        for i in range(len(original_tweets_list)):
            social_support_ranks.append(calculate_social_support_ranks(space, 
                                                                       original_tweets_list[i], 
                                                                       retweets_of_in_comm_list[i])[user_id])
        to_plot.append(social_support_ranks)
    sns.stripplot(data=to_plot, jitter=False)
    plt.xlabel("Overall Bhattacharyya Rank")
    plt.ylabel("Social Support Rank")
    plt.show()


def plot_bhattacharyya_for_top_social_support(space, ds):
    social_support = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm)
    top_social_support = sorted(social_support, key=lambda x: social_support[x], reverse=False)[:10]
    print(top_social_support)
    supply_list = ts_builder.create_mapping_series("supply")
    demand_in_community_list = ts_builder.create_mapping_series("demand_in_community")
    to_plot = []
    for user_id in top_social_support:
        bhattacharyya_ranks = []
        for i in range(len(supply_list)):
            bhattacharyya_ranks.append(calculate_bhattacharyya_ranks(space, ds, 
                                                                     supply_list[i], 
                                                                     demand_in_community_list[i])[user_id])
        to_plot.append(bhattacharyya_ranks)
    sns.stripplot(data=to_plot, jitter=False)
    plt.xlabel("Overall Social Support Rank")
    plt.ylabel("Bhattacharyya Rank")
    plt.show()
    

### Bin Analysis ###################################################################################
def bin_interpretations(market, space, content_type: int, num_comments: int):
    """Print a random sample of <num_comments> comments from the database that have content type 
    <content_type>."""
    np.random.seed(42)
    all_tweets \
        = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
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
    all_tweets \
        = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
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
    all_tweets \
        = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
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
    vectorizer = CountVectorizer(min_df=0.0075)
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
        term_to_weights.append(sorted(term_to_weight, 
                                      key=lambda term: term_to_weight[term], 
                                      reverse=True)[:10])
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


def initialize_channel_hashtag_corpus(market, space, 
                                      tweet_to_hashtags: Dict[int, List[str]], channel):
    """Initialize the corpus for a given channel.
    <market> is a content market. <channel> is a bin number in the binning algorithm.
    The corpus is a list of all the tweets, where each tweet is a string.
    Assume that the preprocessing of the tweets has already been done (i.e. removing numbers and 
    punctuation, stopwords, etc.)"""
    all_tweets \
        = space.original_tweets.union(space.retweets_of_in_comm.union(space.retweets_of_out_comm))
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


### Bhattacharyya Distances - Helpers ##############################################################
def bhattacharyya_distance(dict1, dict2):
    """Calculate the Bhattacharyya distance. 
    <dict1>, <dict2> are dictionaries that map each content type to a set of tweets."""

    # with histogram:
    a = convert_to_relative_frequencies(dict1)
    b = convert_to_relative_frequencies(dict2)
    
    bhattacharyya_coefficient = 0
    for i in range(20):
        if a[i] == 0 or b[i] == 0:
            bhattacharyya_coefficient += 0
        else:
            bhattacharyya_coefficient \
                += np.sqrt(a[i] * b[i])
    if bhattacharyya_coefficient == 0:
        return np.inf
    return -np.log(bhattacharyya_coefficient)


def convert_to_relative_frequencies(d) -> Dict[Any, float]:
    """d is a dictionary that maps each content type to a set of tweets."""
    total = max(1, sum(len(d[content_type]) for content_type in d))
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


### Social Support and Bhattacharyya Over Time #####################################################
def calculate_bhattacharyya_ranks(space, ds, supply, demand_in_community) -> Dict[int, int]:
    """Returns a dictionary mapping each user_id to its Bhattacharyya rank.
    <supply> and <demand_in_community> are dictionaries in the form of the supply and 
    demand_in_community in ContentDemandSupply."""
    all_users = space.producers.union(space.consumers.union(space.core_nodes))
    dict1 = calculate_aggregate_curve(demand_in_community)
    user_id_to_bhattacharyya_distance = {}
    for user in all_users:
        if len(supply[str(user.user_id)]) != 0:
            dict2 = pad_dictionary(supply[str(user.user_id)])
            user_id_to_bhattacharyya_distance[user.user_id] = bhattacharyya_distance(dict1, dict2)

    # create the dictionary
    ranked_ids = list(sorted(user_id_to_bhattacharyya_distance, 
                             key=lambda x: user_id_to_bhattacharyya_distance[x], 
                             reverse=False))
    return {id: ranked_ids.index(id) for id in ranked_ids}


def calculate_aggregate_curve(demand_in_community):
    """Helper function for calculate_bhattacharyya_ranks."""
    dict1 = pad_dictionary(demand_in_community[UserType.CONSUMER]) 
    dict2 = pad_dictionary(demand_in_community[UserType.CORE_NODE])
    for content_type in range(20):
        dict1[content_type] = dict1[content_type].union(dict2[content_type])
    return dict1


def calculate_social_support_ranks(space, original_tweets, retweets_of_in_comm, alpha=1.0) -> Dict[int, int]:
    """Returns a dictionary mapping each user_id to its social support rank.
    <original_tweets> and <retweets_of_in_comm> are sets of the tweets in the form of the original
    tweets and the retweets of in comm in ContentSpace."""
    # TODO: figure out a way to load the producer,
    users = space.producers.union(space.core_nodes.union(space.consumers))
    user_ids = {user.user_id for user in users}
    user_id_to_score = {user_id: [0, 0] for user_id in user_ids}
    friends = create_friends_dict(space, user_ids)
    tweets = [tweet for tweet in original_tweets] + [tweet for tweet in retweets_of_in_comm]
    tweets_by_retweet_group = _group_by_retweet_id(tweets)
    def get_retweets_of_tweet_id(tweet_id):
        return tweets_by_retweet_group.get(tweet_id, [])
    def get_later_retweets_of_tweet_id(tweet_id, created_at):
        return [tweet for tweet in get_retweets_of_tweet_id(tweet_id) 
                if tweet.created_at > created_at]
    def is_direct_follower(a, b):
        # b follows a
        return a in friends.get(b, [])

    for id in tqdm(user_ids):
        user_id_to_score[id][1] = space.get_user(id).global_follower_count
        user_tweets = [tweet for tweet in tweets if tweet.user_id == id]
        original_tweet_ids = [tweet.id for tweet in user_tweets if tweet.retweet_id is None]
        for original_tweet_id in original_tweet_ids:
            retweets = get_retweets_of_tweet_id(original_tweet_id)
            user_id_to_score[id][0] += len(retweets)

            user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]
            for user_retweet in user_retweets:
                retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id, 
                                                          user_retweet.created_at)
                # The person who retweeted is a direct follower of id.
                retweets_from_direct_followers = [rtw for rtw in retweets 
                                                  if is_direct_follower(id, rtw.user_id)]
                user_id_to_score[id][0] += len(retweets_from_direct_followers) * alpha
    
    # create the dictionary
    ranked_ids = list(sorted(user_id_to_score, 
                             key=lambda x: (user_id_to_score[x][0], user_id_to_score[x][1]), 
                             reverse=True))
    return {id: ranked_ids.index(id) for id in ranked_ids}


def create_friends_dict(space, user_ids) -> Dict[int, List[int]]:
    """Helper function for calculate_social_support_ranks."""
    friends = {}
    for user_id in user_ids:
        friends_of_user_id = space.get_user(user_id).local_following
        friends[user_id] = [id for id in friends_of_user_id]
    return friends


def _group_by_retweet_id(tweets) -> Dict[int, List[MinimalTweet]]:
    """Helper function for calculate_social_support_ranks.
    Puts all tweets with the same retweet_id in the same list
    Returns: A dictionary where the key is the retweet_id and 
    the value is the list of tweets with that retweet_id"""
    dict = {}
    for tweet in tweets:
        key = tweet.retweet_id
        if key in dict:
            dict[key].append(tweet)
        else:
            dict[key] = [tweet]

    return dict


# def filter_mapping(ds, mapping: str):
#     """Filter a mapping i.e. supply, demand_in_community, or demand_out_community."""
#     if mapping not in ["demand_in_community", "demand_out_community",
#                         "supply"]:
#         raise KeyError("Invalid Mapping Type.")
    
#     new_mapping = {}
#     for user_type_or_id in vars(ds)[mapping]:
#         new_type_to_tweets = {}
#         for content_type in self.ds.content_space:
#         temp2[content_type.get_representation()] \
#             = self.create_time_series(user_type_or_id, content_type.get_representation(), mapping)


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

    start = datetime(2020, 6, 1)  # datetime(2020, 6, 29)
    end = datetime(2023, 4, 1)  # datetime(2023, 3, 5)  # (2023, 3, 5) is for rachel_chess_content_market
    period = timedelta(days=30)
    ts_builder = TimeSeriesBuilder(ds, space, start, end, period)

    # plot_demand_and_supply(ds, [UserType.CONSUMER, UserType.CORE_NODE], 
    #                        [UserType.PRODUCER, UserType.CORE_NODE])
    
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

    temp = ts_builder.create_mapping_series("supply")
    ts_builder.partition_tweets_by_tweet_type("original_tweets")
    print(sum(len(tweet_set) for tweet_set in ts_builder.partition_tweets_by_tweet_type("original_tweets")))

    # sorted_user_ids = [1330571318971027462, 917892794953404417, 23612012, 3161912605, 227629567, 919900711, 301042394, 228660231, 2233129128, 4369711156, 1884178352, 1651411087, 126345156, 232951413, 277594186, 313299656, 186797066, 92284830, 1729528081, 13247182, 132702118, 77210396, 609121227, 60494861, 1110733580, 3511819222, 46465628, 97426170, 354486695, 161308987, 252909412, 391563229, 277634312, 3392260661, 1081889952412119040, 1356595452, 279565150, 29521967, 94340676, 953260427475079168, 28994084, 1495255914, 1067064666, 4922808130, 75174049, 617004214, 297267701, 1093199136596287489, 83338597, 499173831, 22202577, 31479252, 337149339, 480444935, 406172437, 1702864658, 1167467303002345474, 101850896, 132787956, 434270813, 2609917590, 898166654575751172, 1041446451715473408, 185677963, 769229557576507392, 247232127, 3086225424, 167842102, 60995997, 228806806, 19647809, 198339335, 425376095, 217741900, 1588889406, 71476598]
    # plot_bhattacharyya_distances(ds, sorted_user_ids)

    for user_id in [1330571318971027462, 917892794953404417, 23612012, 3161912605, 227629567, 919900711, 301042394, 228660231, 2233129128, 4369711156, 1884178352, 1651411087, 126345156, 232951413, 277594186, 313299656, 186797066, 92284830, 1729528081, 13247182]:
        plot_bhattacharyya_and_social_support_rank(space, ds, ts_builder, user_id)
    # plot_social_support_for_top_bhattacharyya(space, ds)
    # plot_bhattacharyya_for_top_social_support(space, ds)