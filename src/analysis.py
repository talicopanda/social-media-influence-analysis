from Builder.ContentMarketBuilder import ContentMarketBuilder
from Builder.ContentSpaceBuilder import ContentSpaceBuilder
from Builder.ContentDemandSupplyBuilder import ContentDemandSupplyBuilder
from UserPartitioning import UserPartitioningStrategyFactory
from DAO.DAOFactory import DAOFactory
from User.UserType import UserType
from TS.SimpleTimeSeriesBuilder import SimpleTimeSeriesBuilder
from Tweet.MinimalTweet import MinimalTweet
# from TS.TSATool import *
from Aggregation.ContentSpace import ContentSpace
from Aggregation.ContentDemandSupply import ContentDemandSupply
from Tweet.ContentSpaceTweet import ContentSpaceTweet

from typing import Dict, List, Union, Set, Tuple
import json
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Collection, Dict, Any
import random
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.cluster import KMeans
import math
import re
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from scipy import integrate
from scipy.stats import gaussian_kde, rv_histogram, relfreq, linregress
from datetime import datetime, timedelta
from dateutil import rrule
from tqdm import tqdm
from scipy.stats import rankdata
import sys
import pymongo
from matplotlib.colors import LogNorm


### Final Report Plots #############################################################################
def plot_social_support_rank_and_value(space: ContentSpace, to_plot: List[bool]) -> None:
    """Creates a plot, where the x-axis is the social support rank, and the y-axis is the social 
    support value.
    
    <space> represents the content space we are working with. <to_plot> represents the types of 
    social support we want to show."""
    sorted_user_ids \
        = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, set(), set())
    original_tweet_social_support, retweets_of_in_comm_social_support, \
        retweets_of_out_comm_by_in_comm_social_support, social_support \
        = calculate_social_support(space, space.original_tweets, space.retweets_of_in_comm, set(), set())
    plt.figure()
    if to_plot[0]:
        plt.plot(range(len(sorted_user_ids)), 
                 [original_tweet_social_support[user_id] for user_id in sorted_user_ids], 
                 label="original tweet social support")
    if to_plot[1]:
        plt.plot(range(len(sorted_user_ids)), 
                 [retweets_of_in_comm_social_support[user_id] for user_id in sorted_user_ids], 
                 label="retweet social support")
    if to_plot[2]:
        plt.plot(range(len(sorted_user_ids)), 
                 [retweets_of_out_comm_by_in_comm_social_support[user_id] for user_id in sorted_user_ids], 
                 label="retweet of out comm by in comm social support")
    if to_plot[3]:
        plt.plot(range(len(sorted_user_ids)), 
                 [social_support[user_id] for user_id in sorted_user_ids])
    plt.legend()
    plt.xlabel("Social Support Rank")
    plt.ylabel("Social Support")
    plt.show()


def plot_social_support_and_number_of_followers(space: ContentSpace) -> None:
    """Creates a plot, where the x-axis is the social support rank, and the y-axis is the number of
    people that follow the user (using the create_friends_dict_k) function where k=1. Also prints 
    some stats (the Pearson-r value and the corresponding p-value) for the plot."""
    sorted_user_ids \
        = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, set(), set())
    # sorted_user_ids = sorted(social_supports, key=lambda x: social_supports[x], reverse=False)
    
    friends = create_friends_dict_k(space, sorted_user_ids, k=1)

    # This is to get the followers
    user_id_to_follower_count = {int(user_id): 0 for user_id in sorted_user_ids}
    for user_id in friends:
        for user_id2 in friends[user_id]:
            try:
                user_id_to_follower_count[int(user_id2)] += 1
            except KeyError:
                idx = sorted([(abs(sorted_user_ids[i] - user_id2), i) for i in range(len(sorted_user_ids))])[0]
                user_id_to_follower_count[sorted_user_ids[idx[1]]] += 1
    
    plt.figure()  # reset the figure
    plt.plot(range(len(sorted_user_ids)), 
                [user_id_to_follower_count[user_id] for user_id in sorted_user_ids], label=str(1), 
                color="tab:blue")

    plt.xlabel("Social Support Rank")
    plt.ylabel("Number of Local Followers")
    plt.legend()
    plt.show()
    # print the Pearson-r and corresponding p-value
    print("Stats...")
    print(linregress(list(range(len(sorted_user_ids))), 
                        [user_id_to_follower_count[user_id] for user_id in sorted_user_ids]))


def plot_social_support_and_number_of_followings(space: ContentSpace) -> None:
    """Creates a plot, where the x-axis is the social support rank, and the y-axis is the number of
    people that the user follows (using the create_friends_dict_k) function where k=1. Also prints 
    some stats (the Pearson-r value and the corresponding p-value) for the plot."""
    sorted_user_ids \
        = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, set(), set())
    # sorted_user_ids = sorted(social_supports, key=lambda x: social_supports[x], reverse=False)
    
    friends = create_friends_dict_k(space, sorted_user_ids, k=1)

    # This is to get the followings
    user_id_to_following_count = {}
    for user_id in friends:
        user_id_to_following_count[user_id] = len(friends[user_id])
    
    plt.figure()  # reset the figure
    plt.plot(range(len(sorted_user_ids)), 
                [user_id_to_following_count[user_id] for user_id in sorted_user_ids], label=str(1), 
                color="tab:orange")

    plt.xlabel("Social Support Rank")
    plt.ylabel("Number of Local Followings")
    plt.legend()
    plt.show()
    # print the Pearson-r and corresponding p-value
    print("Stats...")
    print(linregress(list(range(len(sorted_user_ids))), 
                        [user_id_to_following_count[user_id] for user_id in sorted_user_ids]))


def plot_rank_binned_followings(space: ContentSpace, bin_size=20, log=False) -> None:
    """Creates a heatmap, where the x and y-axes represent the different user bins."""
    sorted_user_ids \
        = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, set(), set())
    friends = create_friends_dict(space, sorted_user_ids)

    binned_users = []
    # bin users
    for i in range(len(sorted_user_ids)):
        if i == 0:
            # create a new list
            bin = [sorted_user_ids[i]]
        elif i % bin_size == 0:
            assert len(bin) == bin_size
            binned_users.append(bin)
            bin = [sorted_user_ids[i]]
        else:
            bin.append(sorted_user_ids[i])
    binned_users.append(bin)
    print("Length of binned_users: " + str(len(binned_users)))

    heatmap = []

    # iterate through all the bins
    for b1 in range(len(binned_users)):
        binned_fracs = [[] for _ in range(len(binned_users))]
        # iterate through all the users in each bin
        for user_id in binned_users[b1]:
            binned_followings = [[] for _ in range(len(binned_users))]
            # iterate through all the people that <user_id> follows
            if len(friends[user_id]) == 0:
                continue
            for friend in friends[user_id]:
                for b2 in range(len(binned_users)):
                    if friend in binned_users[b2]:
                        binned_followings[b2].append(friend)
            for b2 in range(len(binned_users)):
                binned_fracs[b2].append(len(binned_followings[b2]) / len(friends[user_id]))
        row = []
        append_row = True
        for b2 in range(len(binned_fracs)):
            if len(binned_fracs[b2]) == 0:
                append_row = False
            else:
                row.append(sum(binned_fracs[b2]) / len(binned_fracs[b2]))
        if append_row:
            heatmap.append(row)
        else:
            # in this case, append a dummy row
            heatmap.append([0 for _ in range(len(binned_users))])
            print("Not included: " + str(b1))

    plt.figure(figsize=(10, 7))
    if not log:
        sns.heatmap(heatmap)
    else:
        sns.heatmap(heatmap, norm=LogNorm())
    plt.ylabel("Bin A")
    plt.xlabel("Bin B")
    plt.title("Average fraction of all the users that a user in Bin A follows that are in Bin B")
    plt.show()


def plot_social_support_rank_and_retweets(space: ContentSpace) -> None:
    """Creates a plot, where the x-axis is the social support rank and the y-axis is a fraction."""
    sorted_user_ids \
        = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, set(), set())

    user_id_to_retweet_in_comm_count = {user_id: 0 for user_id in sorted_user_ids}
    user_id_to_retweet_out_comm_count = {user_id: 0 for user_id in sorted_user_ids}
    user_id_to_retweet_count = {user_id: 0 for user_id in sorted_user_ids}
    
    for tweet in space.retweets_of_in_comm:
        user_id_to_retweet_in_comm_count[tweet.user_id] += 1
        user_id_to_retweet_count[tweet.user_id] += 1
    for tweet in space.retweets_of_out_comm_by_in_comm:
        user_id_to_retweet_out_comm_count[tweet.user_id] += 1
        user_id_to_retweet_count[tweet.user_id] += 1
    new_user_id_to_retweet_count = {}  # prevent zero division error
    for user_id in user_id_to_retweet_count:
        if user_id_to_retweet_count[user_id] == 0:
            new_user_id_to_retweet_count[user_id] = 1
        else:
            new_user_id_to_retweet_count[user_id] = user_id_to_retweet_count[user_id]

    plt.plot(range(len(sorted_user_ids)), 
             [user_id_to_retweet_in_comm_count[user_id] / new_user_id_to_retweet_count[user_id] 
              for user_id in sorted_user_ids], 
             label="retweets in community")
    plt.plot(range(len(sorted_user_ids)), 
             [user_id_to_retweet_out_comm_count[user_id] / new_user_id_to_retweet_count[user_id] 
              for user_id in sorted_user_ids], 
             label="retweets out community")
    plt.axhline(sum([user_id_to_retweet_in_comm_count[user_id] / new_user_id_to_retweet_count[user_id] 
                     for user_id in sorted_user_ids]) / len(sorted_user_ids), color="tab:blue")
    plt.axhline(sum([user_id_to_retweet_out_comm_count[user_id] / new_user_id_to_retweet_count[user_id] 
                     for user_id in sorted_user_ids]) / len(sorted_user_ids), color="tab:orange")
    plt.legend()
    plt.xlabel("Social Support Rank")
    plt.ylabel("Retweet Fraction")
    plt.show()
 

def plot_bhattacharyya_distances(space, ds: ContentDemandSupply) -> None:
    """Creates two plots on the same graph. The x-axis is the social support rank. The left y-axis
    is the Bhattacharyya distance between each user's supply and the aggregate demand. The right 
    y-axis is the total number of original tweets tha the user produces. Also prints some stats (the 
    Pearson-r value and the corresponding p-value) for the plot.
    """
    sorted_user_ids \
        = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, set(), set())

    dict1 = pad_dictionary(ds, ds.demand_in_community[UserType.CONSUMER])
    dict2 = pad_dictionary(ds, ds.demand_in_community[UserType.CORE_NODE])
    for content_type in ds.content_space:
        dict1[content_type.representation] \
            = dict1[content_type.representation].union(dict2[content_type.representation])
        
    curr_rank = 0
    ranks = []
    bhattacharyya_distances = []
    original_tweet_counts = []
    for user_id in sorted_user_ids:
        if len(space.get_user(user_id).original_tweets) >= 10:  # make sure the user has 10+ original tweets
            dict2 = pad_dictionary(ds, ds.supply[user_id])
            if bhattacharyya_distance(ds, dict1, dict2) != np.inf:
                ranks.append(curr_rank)
                bhattacharyya_distances.append(bhattacharyya_distance(ds, dict1, dict2))
                original_tweet_counts.append(len(space.get_user(user_id).original_tweets))
        curr_rank += 1

    fig, ax = plt.subplots()
    ax.plot(ranks, bhattacharyya_distances, color="blue")
    ax.set_xlabel("Rank")
    ax.set_ylabel("Bhattacharyya Distance with In Community Demand", color="blue")

    ax2 = ax.twinx()
    ax2.plot(ranks, original_tweet_counts, color="red")
    # set y-axis label
    ax2.set_ylabel("Number of Original Tweets", color="red")
    plt.show()
    
    # print the Pearson-r and corresponding p-value
    print("Stats...")
    print(linregress(ranks, bhattacharyya_distances))


### Helper Functions for Final Report Plots ########################################################
def calculate_social_support_ranks(space: ContentSpace, 
                                   original_tweets: Set[ContentSpaceTweet], 
                                   retweets_of_in_comm: Set[ContentSpaceTweet], 
                                   retweets_of_out_comm: Set[ContentSpaceTweet], 
                                   retweets_of_out_comm_by_in_comm: Set[ContentSpaceTweet], 
                                   alpha=1.0) -> List[int]:
    """Returns a list of user_ids in descending order of social support rank."""
    users = space.producers.union(space.core_nodes.union(space.consumers))
    user_ids = {user.user_id for user in users}
    user_id_to_score = {user_id: [0, 0] for user_id in user_ids}
    friends = create_friends_dict(space, user_ids)
    tweets \
        = [tweet for tweet in original_tweets] + [tweet for tweet in retweets_of_in_comm] \
            + [tweet for tweet in retweets_of_out_comm] + [tweet for tweet in retweets_of_out_comm_by_in_comm]
    # omit self-retweets
    tweets = [tweet for tweet in tweets if tweet.user_id != tweet.retweet_user_id]
    tweets_by_retweet_group = _group_by_retweet_id(tweets)
    def get_retweets_of_tweet_id(tweet_id):
        return tweets_by_retweet_group.get(tweet_id, [])
    def get_later_retweets_of_tweet_id(tweet_id, created_at):
        return [tweet for tweet in get_retweets_of_tweet_id(tweet_id)
                if tweet.created_at > created_at]
    def is_direct_follower(a, b):
        # b follows a
        return a in friends.get(b, []) or str(a) in friends.get(b, [])

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
    uno = list(sorted(user_id_to_score,
                      key=lambda x: (user_id_to_score[x][0], user_id_to_score[x][1]),
                      reverse=True))
    temp = calculate_social_support(space, original_tweets, retweets_of_in_comm, retweets_of_out_comm, retweets_of_out_comm_by_in_comm)[3]
    dos = list(sorted(temp,
                      key=lambda x: (temp[x], space.get_user(x).global_follower_count),
                      reverse=True))
    uno, dos = {id: uno.index(id) for id in uno}, {id: dos.index(id) for id in dos}
    count = 0
    for user_id in uno:
        if uno[user_id] != dos[user_id]:
            print(user_id)
            count += 1
    print("Testing new social support function...")
    print(count)

    return sorted(uno, key=lambda x: uno[x], reverse=False)


def calculate_social_support(space: ContentSpace, 
                             original_tweets: Set[ContentSpaceTweet], 
                             retweets_of_in_comm: Set[ContentSpaceTweet], 
                             retweets_of_out_comm: Set[ContentSpaceTweet], 
                             retweets_of_out_comm_by_in_comm: Set[ContentSpaceTweet], 
                             alpha=1.0) -> Tuple[Dict[int, int]]:
    """Calculates the social support of each user in <space>, using the <original_tweets>, 
    <retweets_of_in_comm>, <retweets_of_out_comm>, and <retweets_of_out_comm_by_in_comm> that are 
    provided.
    
    Returns a tuple of four different types of dictionaries, in the following order:
        - user_id to the social support score from the original tweets
        - user_id to the social support score from the retweets in community
        - user_id to the social support score from the retweets of out community by in community
        - user_id to the total social support score (which sums the three scores above) 
    """
    users = space.producers.union(space.core_nodes.union(space.consumers))
    user_ids = {user.user_id for user in users}
    user_id_to_original_tweet_score = {user_id: 0 for user_id in user_ids}
    user_id_to_retweet_in_comm_score = {user_id: 0 for user_id in user_ids}
    user_id_to_retweet_out_comm_by_in_comm_score = {user_id: 0 for user_id in user_ids}
    user_id_to_total_score = {user_id: 0 for user_id in user_ids}
    friends = create_friends_dict(space, user_ids)
    tweets \
        = [tweet for tweet in original_tweets] + [tweet for tweet in retweets_of_in_comm] \
            + [tweet for tweet in retweets_of_out_comm] + [tweet for tweet in retweets_of_out_comm_by_in_comm]
    # pmit self-retweets
    tweets = [tweet for tweet in tweets if tweet.user_id != tweet.retweet_user_id]
    tweets_by_retweet_group = _group_by_retweet_id(tweets)
    def get_retweets_of_tweet_id(tweet_id):
        return tweets_by_retweet_group.get(tweet_id, [])
    def get_later_retweets_of_tweet_id(tweet_id, created_at):
        return [tweet for tweet in get_retweets_of_tweet_id(tweet_id)
                if tweet.created_at > created_at]
    def is_direct_follower(a, b):
        # b follows a
        return a in friends.get(b, []) or str(a) in friends.get(b, [])

    for id in tqdm(user_ids):
        user_tweets = [tweet for tweet in tweets if tweet.user_id == id]
        original_tweet_ids = [tweet.id for tweet in user_tweets if tweet.retweet_id is None]
        for original_tweet_id in original_tweet_ids:
            retweets = get_retweets_of_tweet_id(original_tweet_id)
            
            user_id_to_original_tweet_score[id] += len(retweets)
            user_id_to_total_score[id] += len(retweets)

        user_retweets = [tweet for tweet in user_tweets if tweet.retweet_id is not None]
        for user_retweet in user_retweets:
            retweets = get_later_retweets_of_tweet_id(user_retweet.retweet_id,
                                                        user_retweet.created_at)
            # The person who retweeted is a direct follower of id.
            retweets_from_direct_followers = [rtw for rtw in retweets 
                                              if is_direct_follower(id, rtw.user_id)]
            retweets_in_comm_from_direct_followers \
                = [rtw for rtw in retweets 
                   if rtw in retweets_of_in_comm and is_direct_follower(id, rtw.user_id)]
            retweets_out_comm_from_direct_followers \
                = [rtw for rtw in retweets 
                   if rtw in retweets_of_out_comm_by_in_comm and is_direct_follower(id, rtw.user_id)]
            
            user_id_to_retweet_in_comm_score[id] += len(retweets_in_comm_from_direct_followers) * alpha
            user_id_to_retweet_out_comm_by_in_comm_score[id] += len(retweets_out_comm_from_direct_followers) * alpha
            user_id_to_total_score[id] += len(retweets_from_direct_followers) * alpha
        
    return user_id_to_original_tweet_score, user_id_to_retweet_in_comm_score, \
        user_id_to_retweet_out_comm_by_in_comm_score, user_id_to_total_score


def create_friends_dict(space: ContentSpace, user_ids: List[int]) -> Dict[int, List[int]]:
    """Returns a dictionary of user_id to their list of friends.
    A friend of a user u is another user v in the community that u follows.
    """
    friends = {}
    for user_id in user_ids:
        friends_of_user_id = [int(id) for id in space.get_user(user_id).local_following]
        friends[user_id] = [id for id in friends_of_user_id]
    return friends


def create_friends_dict_k(space: ContentSpace, user_ids: List[int], k: int) -> Dict[int, List[int]]:
    """Returns a dictionary of user_id to their list of friends.
    A friend of a user u is another user v in the community that u follows and has retweeted at
    least k of v's original retweets.
    """
    friends = {}
    for user_id in user_ids:
        # at least k retweets
        friends_of_user_id = [int(id) for id in space.get_user(user_id).local_following]
        friends_of_user_id_with_k_retweets = []
        for user_id2 in friends_of_user_id:
            retweet_count = 0
            for tweet in space.get_user(user_id).retweets_of_in_community:
                if tweet.retweet_user_id == user_id2:
                    retweet_count += 1
            if retweet_count >= k:
                friends_of_user_id_with_k_retweets.append(user_id2)
        friends[user_id] = [id for id in friends_of_user_id_with_k_retweets]
    return friends


def _group_by_retweet_id(tweets: List[MinimalTweet]) -> Dict[int, List[MinimalTweet]]:
    """Helper function for calculate_social_support.

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


def bhattacharyya_distance(ds: ContentDemandSupply, 
                           dict1: Dict[Any, Set[MinimalTweet]], 
                           dict2: Dict[Any, Set[MinimalTweet]]) -> float:
    """Calculates the Bhattacharyya distance.
    <dict1>, <dict2> are dictionaries that map each content type representation to a set of tweets.
    """

    a = _convert_to_relative_frequencies(dict1)
    b = _convert_to_relative_frequencies(dict2)

    bhattacharyya_coefficient = 0
    for content_type in ds.content_space:
        if a[content_type.representation] == 0 or b[content_type.representation] == 0:
            bhattacharyya_coefficient += 0
        else:
            bhattacharyya_coefficient \
                += np.sqrt(a[content_type.representation] * b[content_type.representation])
    if bhattacharyya_coefficient == 0:
        return np.inf
    return -np.log(bhattacharyya_coefficient)


def _convert_to_relative_frequencies(d: Dict[Any, Set[MinimalTweet]]) -> Dict[Any, float]:
    """Helper function for bhattacharyya_distance.
    
    <d> is a dictionary that maps each content type to a set of tweets."""
    # prevent zero division error
    total = max(1, sum(len(d[content_type_repr]) for content_type_repr in d))
    content_type_to_relative_frequency = {}
    for content_type_repr in d:
        content_type_to_relative_frequency[content_type_repr] = len(d[content_type_repr]) / total
    return content_type_to_relative_frequency


def pad_dictionary(ds: ContentDemandSupply, d: Dict[Any, Set[MinimalTweet]]) \
    -> Dict[Any, Set[MinimalTweet]]:
    """For content types that are not in the dictionary, add a key corresponding to the content type
    and an empty set.
    
    <d> is a dictionary that maps each content type representation to a set of tweets."""
    padded_dict = {}
    for content_type in ds.content_space:
        if content_type.representation in d:
            padded_dict[content_type.representation] = d[content_type.representation]
        else:
            padded_dict[content_type.representation] = set()
    return padded_dict


### Other Useful Functions #########################################################################




### Plotting Functions #############################################################################
def plot_demand_and_supply_binning(ds,  
                                   supply_keys: Collection[Union[UserType, int]],
                                   demand_in_community_keys: Collection[Union[UserType, int]],
                                   demand_out_community_keys: Collection[Union[UserType, int]],
                                   demand_out_community_by_in_community_keys: Collection[Union[UserType, int]]):
    """Plot the demand and supply curves for the binning embedding."""
    # print(ds.demand_in_community.keys())
    # TODO: get rid of this
    demand = {user_type: {i: 0 for i in range(len(ds.content_space))} for user_type in [UserType.CONSUMER, UserType.CORE_NODE]}
    # core_node_demand = {i: 0 for i in range(len(ds.content_space))}
    # do not get rid of this
    
    supply_colours = ["red", "yellow"]
    i = 0
    for key in supply_keys:
        print(ds.supply[key].keys())
        plt.bar(sorted(ds.supply[key].keys()),
                [len(ds.supply[key][content_type])
                 for content_type in sorted(ds.supply[key].keys())],
                alpha=1, label=key.value, edgecolor=supply_colours[i], fill=False)
        i += 1

    demand_colours = ["blue", "green"]
    i = 0
    for key in demand_in_community_keys:
        print(sorted(ds.demand_in_community[key].keys()))
        # TODO: get rid of this
        for content_type in sorted(ds.demand_in_community[key].keys()):
            demand[key][content_type] += len(ds.demand_in_community[key][content_type])
        # do not get rid of this
        # plt.bar(sorted(ds.demand_in_community[key].keys()), 
        #         [len(ds.demand_in_community[key][content_type]) 
        #          for content_type in sorted(ds.demand_in_community[key].keys())],
        #         alpha=1, label=key.value, edgecolor=demand_colours[i], fill=False)
        i += 1
        
    for key in demand_out_community_by_in_community_keys:
        print(sorted(ds.demand_out_community_by_in_community[key].keys()))
        # TODO: get rid of this
        for content_type in sorted(ds.demand_out_community_by_in_community[key].keys()):
            demand[key][content_type] += len(ds.demand_out_community_by_in_community[key][content_type])
        # do not get rid of this
        # plt.bar(sorted(ds.demand_out_community_by_in_community[key].keys()), 
        #         [len(ds.demand_out_community_by_in_community[key][content_type]) 
        #          for content_type in sorted(ds.demand_out_community_by_in_community[key].keys())],
        #         alpha=1, label=key.value)
    
    # TODO: get rid of this
    i = 0
    for key in [UserType.CONSUMER, UserType.CORE_NODE]:
        plt.bar(sorted(demand[key].keys()),
                [demand[key][content_type]
                 for content_type in sorted(demand[key].keys())],
                alpha=1, label=key.value, edgecolor=demand_colours[i], fill=False)
        i += 1
    # do not get rid of this

    plt.legend()
    plt.show()


def plot_demand_and_supply_creator(ds,  
                                   supply_keys: Collection[Union[UserType, int]],
                                   demand_in_community_keys: Collection[Union[UserType, int]],
                                   demand_out_community_keys: Collection[Union[UserType, int]]):
    """Plot the demand and supply curves for the creator embedding."""
    # map each user to a number
    users = ds.producers.union(ds.consumers.union(ds.core_nodes))
    sorted_users = sorted(list(users), key=lambda user: user.user_id)
    user_id_to_num = {user.user_id: sorted_users.index(user) for user in sorted_users}
    
    supply_colours = ["red", "yellow"]
    i = 0
    for key in supply_keys:
        # print(ds.supply[key].keys())
        plt.bar([user_id_to_num[user_id] for user_id in sorted(ds.supply[key].keys())],
                [len(ds.supply[key][content_type])
                 for content_type in sorted(ds.supply[key].keys())],
                alpha=1, label=key.value, edgecolor=supply_colours[i], fill=False)
        i += 1

    demand_in_community_colours = ["blue", "green"]
    i = 0
    for key in demand_in_community_keys:
        # print(sorted(ds.demand_in_community[key].keys()))
        # TODO: get rid of this
        # for content_type in sorted(ds.demand_in_community[key].keys()):
        #     demand[content_type] += len(ds.demand_in_community[key][content_type])
        # do not get rid of this
        plt.bar([user_id_to_num[user_id] for user_id in sorted(ds.demand_in_community[key].keys())], 
                [len(ds.demand_in_community[key][content_type]) 
                 for content_type in sorted(ds.demand_in_community[key].keys())],
                alpha=1, label=key.value, edgecolor=demand_in_community_colours[i], fill=False)
        i += 1
        
    for key in demand_out_community_keys:
        # print(sorted(ds.demand_out_community[key].keys()))
        # TODO: get rid of this
        # for content_type in sorted(ds.demand_out_community[key].keys()):
        #     demand[content_type] += len(ds.demand_out_community[key][content_type])
        # do not get rid of this
        plt.bar([user_id_to_num[user_id] for user_id in sorted(ds.demand_out_community[key].keys())], 
                [len(ds.demand_out_community[key][content_type]) 
                 for content_type in sorted(ds.demand_out_community[key].keys())],
                alpha=0.3, label=key.value)
    
    # TODO: get rid of this
    # plt.bar(sorted(demand.keys()), [demand[content_type] for content_type in sorted(demand.keys())],
    #         alpha=0.3, label="all demand")
    # do not get rid of this

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


def plot_bhattacharyya_and_social_support_rank(space, ds, ts_builder, user_id: int):
    supply_list = ts_builder.create_mapping_series("supply")
    demand_in_community_list = ts_builder.create_mapping_series("demand_in_community")
    demand_out_community_list = ts_builder.create_mapping_series("demand_out_community")
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    retweets_of_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")

    bhattacharyya_ranks, social_support_ranks = [], []
    for i in range(len(supply_list)):
        bhattacharyya_rank \
            = calculate_bhattacharyya_ranks(space, ds, supply_list[i], demand_in_community_list[i], demand_out_community_list[i])[user_id]
        social_support_rank \
            = calculate_social_support_ranks(space, original_tweets_list[i], retweets_of_in_comm_list[i])[user_id]
        bhattacharyya_ranks.append(bhattacharyya_rank)
        social_support_ranks.append(social_support_rank)
    plt.figure(figsize=(10, 5))
    plt.plot(ts_builder.time_stamps, bhattacharyya_ranks, label="Bhattacharyya Rank", color="tab:blue")
    plt.plot(ts_builder.time_stamps, social_support_ranks, label="Social Support Rank", color="tab:orange")
    plt.legend()
    plt.ylabel("Rank")
    plt.title("user_id: " + str(user_id))
    # plt.show()
    plt.savefig("../results/bhattacharyya_and_social_support_" + str(user_id))


def plot_bhattacharyya_and_social_support_agg(space, ds, ts_builder, user_ids: List[int]):
    """Averages the ranks of the users for each of the time periods."""
    supply_list = ts_builder.create_mapping_series("supply")
    demand_in_community_list = ts_builder.create_mapping_series("demand_in_community")
    demand_out_community_by_in_community_list = ts_builder.create_mapping_series("demand_out_community_by_in_community")
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    retweets_of_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")
    retweets_of_out_comm_by_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_out_comm_by_in_comm")

    bhattacharyya_ranks, social_support_ranks = [], []
    for i in range(len(supply_list)):
        bhattacharyya_rank_sum = 0
        social_support_rank_sum = 0
        for user_id in user_ids:
            bhattacharyya_rank_sum \
                += calculate_bhattacharyya_ranks(space, ds, supply_list[i], demand_in_community_list[i], demand_out_community_by_in_community_list[i])[user_id]
            social_support_rank_sum \
                += calculate_social_support_ranks(space, original_tweets_list[i], retweets_of_in_comm_list[i], retweets_of_out_comm_by_in_comm_list[i])[user_id]
        bhattacharyya_ranks.append(bhattacharyya_rank_sum / len(user_ids))
        social_support_ranks.append(social_support_rank_sum / len(user_ids))
    plt.figure(figsize=(10, 5))
    plt.plot(ts_builder.time_stamps, bhattacharyya_ranks, label="Bhattacharyya Rank", color="tab:blue")
    plt.plot(ts_builder.time_stamps, social_support_ranks, label="Social Support Rank", color="tab:orange")
    plt.ylim((0, 76))
    plt.legend()
    plt.ylabel("Rank")
    plt.title("Top 5 Overall Social Support")
    plt.show()
    

def plot_social_support_for_top_bhattacharyya(space, ds):
    bhattacharyyas = calculate_bhattacharyya_ranks(space, ds, ds.supply, ds.demand_in_community)
    top_bhattacharyyas = sorted(bhattacharyyas, key=lambda x: bhattacharyyas[x], reverse=False)[:10]
    # print(top_bhattacharyyas)
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    retweets_of_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")
    retweets_of_out_comm_by_in_comm_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_out_comm_by_in_comm")
    to_plot = []
    for user_id in top_bhattacharyyas:
        social_support_ranks = []
        for i in range(len(original_tweets_list)):
            social_support_ranks.append(calculate_social_support_ranks(space,
                                                                       original_tweets_list[i],
                                                                       retweets_of_in_comm_list[i],
                                                                       retweets_of_out_comm_by_in_comm_list[i])[user_id])
        to_plot.append(social_support_ranks)
    sns.stripplot(data=to_plot, jitter=False)
    plt.xlabel("Overall Bhattacharyya Rank")
    plt.ylabel("Social Support Rank")
    plt.show()


def plot_bhattacharyya_for_top_social_support(space, ds):
    social_supports = calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm, space.retweets_of_out_comm_by_in_comm)
    top_social_supports = sorted(top_social_supports, key=lambda x: top_social_supports[x], reverse=False)[:10]
    supply_list = ts_builder.create_mapping_series("supply")
    demand_in_community_list = ts_builder.create_mapping_series("demand_in_community")
    to_plot = []
    for user_id in top_social_supports:
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


def plot_bhattacharyya_and_number_of_followers(space, ds):
    all_users = space.producers.union(space.consumers.union(space.core_nodes))
    bhattacharyyas = calculate_bhattacharyya_ranks(space, ds, ds.supply, ds.demand_in_community, ds.demand_out_community)
    bhattacharyyas = sorted(bhattacharyyas, key=lambda x: bhattacharyyas[x], reverse=False)
    local_follower_counts = {user.user_id: user.local_follower_count for user in all_users}
    local_follower_counts = [local_follower_counts[user_id] for user_id in bhattacharyyas]
    plt.plot(range(len(bhattacharyyas)), local_follower_counts)
    plt.xlabel("Social Support Rank")
    plt.ylabel("Number of Local Followers")
    print(np.corrcoef(list(range(len(bhattacharyyas))), local_follower_counts))
    plt.show()


def plot_tweet_proportion_over_time(ts_builder, user_id):
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")

    tweet_counts = [len(tweet_set) for tweet_set in original_tweets_list]
    tweet_counts_normed = [float(tweet_count) / sum(tweet_counts) 
                           for tweet_count in tweet_counts]

    user_tweet_counts = []
    for tweet_set in original_tweets_list:
        user_tweet_counts.append(len([tweet for tweet in tweet_set if tweet.user_id == user_id]))
    user_tweet_counts_normed = [float(tweet_count) / sum(user_tweet_counts) 
                                for tweet_count in user_tweet_counts]

    plt.plot(ts_builder.time_stamps, tweet_counts_normed, 
             label="original tweets overall", color="black")
    plt.plot(ts_builder.time_stamps, user_tweet_counts_normed, 
             label="original tweets " + str(user_id), color="red")
    plt.legend()
    plt.show()


def plot_tweet_count_over_time(ts_builder, user_id):
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    tweet_counts = [len(tweet_set) for tweet_set in original_tweets_list]
    retweets_in_community_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")
    retweet_in_community_counts = [len(tweet_set) for tweet_set in retweets_in_community_list]
    # retweet_of_out_community_by_in_community_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_out_comm_by_in_comm")
    # retweet_of_out_community_by_in_community_counts = [len(tweet_set) for tweet_set in retweet_of_out_community_by_in_community_list]
    # retweet_counts = [retweet_in_community_counts[i] + retweet_of_out_community_by_in_community_counts[i] 
    #                   for i in range(len(retweet_in_community_counts))]
    
    user_tweet_counts = []
    for tweet_set in original_tweets_list:
        user_tweet_counts.append(len([tweet for tweet in tweet_set if tweet.user_id == user_id]))

    plt.plot(ts_builder.time_stamps, tweet_counts, label="original tweets")
    plt.plot(ts_builder.time_stamps, retweet_in_community_counts, label="retweets in community")
    # plt.plot(ts_builder.time_stamps, retweet_counts, label="all retweets")
    # plt.plot(ts_builder.time_stamps, user_tweet_counts, 
    #          label="original tweets " + str(user_id))
    plt.legend()
    plt.show()

    return sum(user_tweet_counts)


def plot_kmeans_inertia(embeddings: Dict[int, List]):
    """ 
    Elbow method to find a good value of k:

    A good model is one with low inertia AND a low number of clusters (K). 
    However, this is a tradeoff because as K increases, inertia decreases.

    See the graph outputted and find the k where the decrease in inertia begins to slow.
    In other words, where the graph starts to platoe.
    """
    inertias = []

    min_k = 1
    # max_k = len(embeddings) // 20  # 5% of data size to observe a trend
    max_k = 100

    print(
        f"Choosing best k value for kmeans in the range. Checking from k = {min_k} to k = {max_k}...")

    # https://stackoverflow.com/questions/835092/python-dictionary-are-keys-and-values-always-the-same-order
    data = np.asarray(list(embeddings.values()), dtype=np.float32)
    print("k = ", end=' ')
    for i in range(min_k, max_k):
        print(i, end=' ')
        sys.stdout.flush()
        kmeans = KMeans(n_clusters=i, n_init="auto")
        kmeans.fit(data)
        inertias.append(kmeans.inertia_)
    print()

    plt.plot(range(min_k, max_k), inertias, marker='o')
    plt.title('Elbow method')
    plt.xlabel('Number of clusters')
    plt.ylabel('Inertia')
    plt.show()
    print("Plot also saved under /experiments/kmeans_plot.png for convenience")
    plt.savefig("../experiments/kmeans_plot.png")


    print(len(space.retweets_of_out_comm_by_in_comm))
    og, in_comm, out_comm, tot = calculate_social_support(space, space.original_tweets,
                                                                  space.retweets_of_in_comm,
                                                                  space.retweets_of_out_comm,
                                                                  space.retweets_of_out_comm_by_in_comm)
    plt.plot(range(len(sorted_user_ids)), [og[user_id] for user_id in sorted_user_ids], 
             label="original tweet social support"
             )
    plt.plot(range(len(sorted_user_ids)), [in_comm[user_id] for user_id in sorted_user_ids], 
             label="retweet social support"
             )
    plt.legend()
    plt.xlabel("Social Support Rank")
    plt.ylabel("Social Support")
    plt.show()
   

def plot_producers_and_consumers_followings(space, sorted_user_ids):
    """Assume for now that the top 10 user_ids are the core nodes."""
    friends = create_friends_dict_2(space, sorted_user_ids, k=1)

    core_node_user_ids = sorted_user_ids[:10]
    other_user_ids = sorted_user_ids[10:]

    core_node_fracs, other_user_fracs = [], []
    for user_id in other_user_ids:
        core_node_followings, other_user_followings = [], []
        for friend in friends[user_id]:
            if friend in core_node_user_ids:
                core_node_followings.append(friend)
            else:
                other_user_followings.append(friend)
        core_node_fracs.append(len(core_node_followings) / 10)
        other_user_fracs.append(len(other_user_followings) / len(sorted_user_ids[10:]))
    
    plt.plot(range(10, len(sorted_user_ids)), core_node_fracs, label="core node fraction")
    plt.plot(range(10, len(sorted_user_ids)), other_user_fracs, label="producer / consumer fraction")
    print("Average core node fraction: " + str(sum(core_node_fracs) / len(core_node_fracs)))
    print("Average other user fraction: " + str(sum(other_user_fracs) / len(other_user_fracs)))
    plt.xlabel("Social Support Rank")
    plt.ylabel("Fraction")
    plt.legend()
    plt.show()


def plot_rank_binned_and_mean_bin_number(space, sorted_user_ids, bin_size=20):
    friends = create_friends_dict_2(space, sorted_user_ids, k=1)

    binned_users = []
    # bin users
    for i in range(len(sorted_user_ids)):
        if i == 0:
            # create a new list
            bin = [sorted_user_ids[i]]
        elif i % bin_size == 0:
            assert len(bin) == bin_size
            binned_users.append(bin)
            bin = [sorted_user_ids[i]]
        else:
            bin.append(sorted_user_ids[i])
    binned_users.append(bin)
    print("Length of binned_users: " + str(len(binned_users)))

    included_bins = []
    mean_bins_b = []

    # iterate through all the bins
    for b1 in range(len(binned_users)):
        binned_fracs = [[] for _ in range(len(binned_users))]
        # iterate through all the users in each bin
        for user_id in binned_users[b1]:
            binned_followings = [[] for _ in range(len(binned_users))]
            # iterate through all the people that <user_id> follows
            if len(friends[user_id]) == 0:
                continue
            for friend in friends[user_id]:
                for b2 in range(len(binned_users)):
                    if friend in binned_users[b2]:
                        binned_followings[b2].append(friend)
            for b2 in range(len(binned_users)):
                binned_fracs[b2].append(len(binned_followings[b2]) / len(friends[user_id]))
        row = []
        append_row = True
        for b2 in range(len(binned_fracs)):
            if len(binned_fracs[b2]) == 0:
                append_row = False
            else:
                row.append(sum(binned_fracs[b2]) / len(binned_fracs[b2]))
        if append_row:
            mean_bins_b.append(sum(i * row[i] for i in range(len(row))))
            included_bins.append(b1)
        else:
            print("Not included: " + str(b1))
    
    plt.figure()
    plt.plot(included_bins, mean_bins_b)
    plt.xlabel("Bin A")
    plt.ylabel("Mean Bin B")
    plt.title("ML 1, binsize = " + str(bin_size))
    plt.savefig("../results/ml_content_market_1_mean_bin_b_binsize_" + str(bin_size))
    # plt.show()


def plot_bin_fraction_over_time(space):
    tweets = space.original_tweets.union(space.retweets_of_in_comm)
    for content_type in space.content_space:
        curr_repr = content_type.representation
        month_to_count_total = {}
        month_to_count_content_type = {}
        for tweet in tweets:  # we iterate through tweets instead of using the ContentTypeMapping because we might want to include a different subset of tweets
            month = datetime(tweet.created_at.year, tweet.created_at.month, 1)
            
            # for month_to_count_total
            if month in month_to_count_total:
                month_to_count_total[month] += 1
            else:
                month_to_count_total[month] = 1

            # for month_to_count_content_type
            if tweet.content.representation == curr_repr:
                if month in month_to_count_content_type:
                    month_to_count_content_type[month] += 1
                else:
                    month_to_count_content_type[month] = 1
            else:
                if month in month_to_count_content_type:
                    continue
                else:
                    month_to_count_content_type[month] = 0
        
        month_to_count_frac = {}
        for month in month_to_count_total:
            if month_to_count_total[month] == 0:
                continue
            else:
                month_to_count_frac[month] = month_to_count_content_type[month] / month_to_count_total[month]
        
        plt.figure(figsize=(10, 7))
        plt.plot(sorted(month_to_count_frac), [month_to_count_frac[month] for month in sorted(month_to_count_frac)])
        plt.title(curr_repr)
        plt.savefig("../results/binning over time/ml_content_market_1_binning_" + str(curr_repr))


def original_tweets_to_retweets_ratio(market):
    users = market.producers.union(market.consumers.union(market.core_nodes))
    ratios = []
    for user in users:
        if len(user.retweets_of_in_community) != 0:
            ratios.append(len(user.original_tweets) / (len(user.retweets_of_in_community)))
    print(sum(ratios) / len(ratios))


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
    for i in range(12):
        corpus.extend(initialize_channel_corpus(market, space, i))
    return corpus


### Relative Frequency - Words #####################################################################
def relative_frequency(market, space):
    corpus = initialize_market_corpus(market, space)
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    X = X.todense()
    X = np.array(X)

    term_freqs = np.count_nonzero(X, axis=0)  # X.sum(axis=0)
    term_list = vectorizer.get_feature_names_out()
    print(len(term_list))

    bin_counts = []
    for i in range(12):
        bin_counts.append(number_of_tweets_in_bin(market, space, i))
    bin_boundaries = [0]
    sum_so_far = 0
    for i in range(12):
        sum_so_far += bin_counts[i]
        bin_boundaries.append(sum_so_far)

    term_to_weights = []
    for i in range(12):
        term_to_weight = {}
        term_freqs_in_channel = X[bin_boundaries[i]:bin_boundaries[i + 1]].sum(axis=0)  # np.count_nonzero(X[bin_boundaries[i]:bin_boundaries[i + 1]], axis=0)
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


### Relative Frequency and TF-IDF - Words Per Month ################################################
def relative_frequency_months(market):
    corpus = initialize_month_corpus(market)
    vectorizer = CountVectorizer(stop_words="english", min_df=100, ngram_range=(1, 2))
    X = vectorizer.fit_transform(corpus)
    X = X.todense()
    X = np.array(X)

    term_freqs = X.sum(axis=0)  # np.count_nonzero(X, axis=0)
    term_list = vectorizer.get_feature_names_out()
    print(len(term_list))

    month_counts = []
    for month in get_all_months(market):
        month_counts.append(number_of_tweets_in_month(market, month))
    month_boundaries = [0]
    sum_so_far = 0
    for i in range(len(get_all_months(market))):
        sum_so_far += month_counts[i]
        month_boundaries.append(sum_so_far)

    # check that threshold passed in every month
    # threshold = 10
    # monthly_sums = []
    # for i in range(len(get_all_months(market))):
    #     monthly_sums.append(list(X[month_boundaries[i]:month_boundaries[i + 1]].sum(axis=0)))
    # monthly_sums = np.array(monthly_sums)
    # good_idxs = set()
    # for j in range(len(term_list)):
    #     if all(monthly_sums[1:-1, j] >= threshold):
    #         good_idxs.add(j)
    # print("Number of good terms: " + str(len(good_idxs)))
    

    term_to_weights = []
    for i in range(len(get_all_months(market))):
        good_words = 0
        term_to_weight = {}
        term_freqs_in_month = X[month_boundaries[i]:month_boundaries[i + 1]].sum(axis=0)  # np.count_nonzero(X[bin_boundaries[i]:bin_boundaries[i + 1]], axis=0)
        rel_freqs = term_freqs_in_month / term_freqs
        for j in range(len(term_list)):
            # check that the term is one that passes the threshold
            if term_freqs_in_month[j] >= 100:
                good_words += 1
                term_to_weight[term_list[j]] = rel_freqs[j]
            else:
                term_to_weight[term_list[j]] = 0
        term_to_weights.append(sorted(term_to_weight,
                                      key=lambda term: term_to_weight[term],
                                      reverse=True)[:10])
        print(get_all_months(market)[i])
        print(sorted(term_to_weight, key=lambda term: term_to_weight[term], reverse=True)[:10])
        print(good_words)

    return term_to_weights


def number_of_tweets_in_month(market, month: tuple[int]):
    all_tweets \
        = market.original_tweets \
            .union(market.retweets_of_in_comm.union(market.retweets_of_out_comm_by_in_comm))
    count = 0
    for tweet in all_tweets:
        if month ==  (tweet.created_at.year, tweet.created_at.month):
            count += 1
    return count


def initialize_month_corpus(market):
    """A corpus is a list.
    Each element in the list is a tweet.
    The corpus is sorted so that the tweets in the earlier months come first"""
    month_to_text = {}
    corpus = []
    all_tweets \
        = market.original_tweets \
            .union(market.retweets_of_in_comm.union(market.retweets_of_out_comm_by_in_comm))
    for tweet in all_tweets:
        month = (tweet.created_at.year, tweet.created_at.month)
        if month in month_to_text:
            month_to_text[month].append(tweet.content)
        else:
            month_to_text[month] = [tweet.content]
    for month in sorted(month_to_text):
        corpus.extend(month_to_text[month])
    return corpus


def get_all_months(market):
    all_tweets \
        = market.original_tweets \
            .union(market.retweets_of_in_comm.union(market.retweets_of_out_comm_by_in_comm))
    return sorted(list({(tweet.created_at.year, tweet.created_at.month) for tweet in all_tweets}))


### Bhattacharyya Distances - Helpers ##############################################################



### Social Support and Bhattacharyya Over Time #####################################################
def _rank_dict(dct: Dict, reverse: bool) -> Dict:
    # Convert Dictionary to 2D array
    key_list = []
    value_list = []
    for key, val in dct.items():
        key_list.append(key)
        value_list.append(val)

    # Rank
    rank_list = rankdata(value_list, method="average")
    if reverse:
        rank_list = len(rank_list) + 1 - rank_list

    # Convert back to Dictionary
    return dict(zip(key_list, rank_list))


def calculate_bhattacharyya_ranks(space, ds, supply, demand_in_community, demand_out_community) -> Dict[int, int]:
    """Returns a dictionary mapping each user_id to its Bhattacharyya rank.
    <supply> and <demand_in_community> are dictionaries in the form of the supply and
    demand_in_community in ContentDemandSupply."""
    all_users = space.producers.union(space.consumers.union(space.core_nodes))
    dict1 = calculate_aggregate_curve(ds, demand_in_community, demand_out_community)
    user_id_to_bhattacharyya_distance = {}
    for user in all_users:
        # if len(supply[user.user_id]) != 0:
        dict2 = pad_dictionary(ds ,supply[user.user_id])
        user_id_to_bhattacharyya_distance[user.user_id] = bhattacharyya_distance(ds, dict1, dict2)

    # create the dictionary
    ranked_ids = list(sorted(user_id_to_bhattacharyya_distance,
                             key=lambda x: (user_id_to_bhattacharyya_distance[x], x),
                             reverse=False))
    return {id: ranked_ids.index(id) for id in ranked_ids}
    # return _rank_dict(user_id_to_bhattacharyya_distance, reverse=False)


def calculate_aggregate_curve(ds, demand_in_community, demand_out_community):
    """Helper function for calculate_bhattacharyya_ranks."""
    dict1 = pad_dictionary(ds, demand_in_community[UserType.CONSUMER])
    dict2 = pad_dictionary(ds, demand_in_community[UserType.CORE_NODE])
    # TODO: get rid of this
    # dict3 = pad_dictionary(demand_out_community[UserType.CONSUMER]) 
    # dict4 = pad_dictionary(demand_out_community[UserType.CORE_NODE])
    # do not get rid of this
    for content_type in ds.content_space:
        dict1[content_type.representation] \
            = dict1[content_type.representation].union(dict2[content_type.representation])
        # dict1[content_type] \
        #     = dict1[content_type].union(dict2[content_type].union(dict3[content_type].union(dict4[content_type])))
    return dict1

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

    # temp = {}
    # for content_type in ds.supply["1330571318971027462"]:
    #     temp[content_type] = len(ds.supply["1330571318971027462"][content_type])
    # print(temp)

    start = datetime(2020, 6, 1)  # datetime(2020, 6, 29)
    end = datetime(2023, 4, 1)  # datetime(2023, 3, 5)  # (2023, 3, 5) is for rachel_chess_content_market
    period = timedelta(days=30)
    ts_builder = SimpleTimeSeriesBuilder(ds, space, start, end, period)

    plot_demand_and_supply(ds,
                           [UserType.PRODUCER, UserType.CORE_NODE], 
                           [UserType.CONSUMER, UserType.CORE_NODE],
                           [])
    print(ds.demand_out_community)
    
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

    # temp = ts_builder.create_mapping_series("supply")
    # ts_builder.partition_tweets_by_tweet_type("original_tweets")
    # print(sum(len(tweet_set) for tweet_set in ts_builder.partition_tweets_by_tweet_type("original_tweets")))

    sorted_user_ids = [1330571318971027462, 917892794953404417, 23612012, 3161912605, 227629567, 
                       919900711, 301042394, 228660231, 2233129128, 4369711156, 
                       1884178352, 1651411087, 126345156, 232951413, 277594186, 
                       313299656, 186797066, 92284830, 1729528081, 13247182, 
                       132702118, 77210396, 609121227, 60494861, 1110733580, 
                       3511819222, 46465628, 97426170, 354486695, 161308987, 
                       252909412, 391563229, 277634312, 3392260661, 1081889952412119040, 
                       1356595452, 279565150, 29521967, 94340676, 953260427475079168, 
                       28994084, 1495255914, 1067064666, 4922808130, 75174049, 
                       617004214, 297267701, 1093199136596287489, 83338597, 499173831, 
                       22202577, 31479252, 337149339, 480444935, 406172437, 
                       1702864658, 1167467303002345474, 101850896, 132787956, 434270813, 
                       2609917590, 898166654575751172, 1041446451715473408, 185677963, 769229557576507392, 
                       247232127, 3086225424, 167842102, 60995997, 228806806, 
                       19647809, 198339335, 425376095, 217741900, 1588889406, 
                       71476598]
    # plot_bhattacharyya_distances(ds, sorted_user_ids)

    # print(calculate_social_support_ranks(space, space.original_tweets, space.retweets_of_in_comm))

    # user_ids = [19647809, 198339335, 425376095, 217741900, 1588889406, 71476598]
    # plot_bhattacharyya_and_social_support_agg(
    #     space, ds, ts_builder, 
    #     [1330571318971027462, 917892794953404417, 23612012, 3161912605, 227629567]
    # )
    # plot_social_support_for_top_bhattacharyya(space, ds)
    # plot_bhattacharyya_for_top_social_support(space, ds)

    # plot_social_support_and_number_of_followers(space)

    # tweet_count_over_time(ts_builder, 919900711)