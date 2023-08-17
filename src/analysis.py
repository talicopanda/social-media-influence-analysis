from User.UserType import UserType
from TS.SimpleTimeSeriesBuilder import SimpleTimeSeriesBuilder
from Tweet.MinimalTweet import MinimalTweet
from Aggregation.ContentMarket import ContentMarket
from Aggregation.ContentSpace import ContentSpace
from Aggregation.ContentDemandSupply import ContentDemandSupply
from Tweet.ContentSpaceTweet import ContentSpaceTweet

from typing import Dict, List, Union, Set, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
from typing import Dict, Any, DefaultDict
import numpy as np
from scipy.stats import linregress
from tqdm import tqdm
from matplotlib.colors import LogNorm
from sklearn.feature_extraction.text import CountVectorizer


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


def relative_frequency_months(market: ContentMarket) -> None:
    """Calculates the relative frequency of each word in the set of tweets.
    
    Prints the top 10 words for each month in <market>.
    """
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

    term_to_weights = []
    for i in range(len(get_all_months(market))):
        good_words = 0
        term_to_weight = {}
        term_freqs_in_month = X[month_boundaries[i]:month_boundaries[i + 1]].sum(axis=0)
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


def number_of_tweets_in_month(market: ContentMarket, month: tuple[int]) -> int:
    """Returns the number of tweets in <month> that are in <market>.
    <month> is a tuple of two integers in the format of (year, month) (ex. (2023, 8) would represent
    August 2023)."""
    all_tweets \
        = market.original_tweets \
            .union(market.retweets_of_in_comm.union(market.retweets_of_out_comm_by_in_comm))
    count = 0
    for tweet in all_tweets:
        if month ==  (tweet.created_at.year, tweet.created_at.month):
            count += 1
    return count


def initialize_month_corpus(market: ContentMarket) -> List[List[str]]:
    """Creates and returns the corpus for all the tweets.
    
    A corpus is a list. Each element in the list is a list of all the tweets in that month.
    The corpus is sorted so that the tweets in the earlier months come first."""
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


def get_all_months(market: ContentMarket) -> List[tuple[int]]:
    """Get a list of all the different months in which a tweet in <market> was created."""
    all_tweets \
        = market.original_tweets \
            .union(market.retweets_of_in_comm.union(market.retweets_of_out_comm_by_in_comm))
    return sorted(list({(tweet.created_at.year, tweet.created_at.month) for tweet in all_tweets}))


### Helper Functions for Final Report Plots ########################################################
def calculate_social_support_ranks(space: ContentSpace, 
                                   original_tweets: Set[ContentSpaceTweet], 
                                   retweets_of_in_comm: Set[ContentSpaceTweet], 
                                   retweets_of_out_comm: Set[ContentSpaceTweet], 
                                   retweets_of_out_comm_by_in_comm: Set[ContentSpaceTweet]) \
                                    -> List[int]:
    """Returns a list of user_ids in descending order of social support rank."""
    total_social_support \
        = calculate_social_support(space, original_tweets, retweets_of_in_comm, retweets_of_out_comm, 
                                   retweets_of_out_comm_by_in_comm)[3]
    social_support_ranks \
        = list(sorted(total_social_support,
                      key=lambda x: (total_social_support[x], space.get_user(x).global_follower_count),
                      reverse=True))
    return social_support_ranks


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
def calculate_bhattacharyya_ranks(space: ContentSpace, 
                                  ds: ContentDemandSupply, 
                                  supply: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]], 
                                  demand_in_community: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]], 
                                  demand_out_community: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]]) \
                                    -> Dict[int, int]:
    """Returns a dictionary mapping each user_id to its Bhattacharyya rank."""
    all_users = space.producers.union(space.consumers.union(space.core_nodes))
    dict1 = calculate_aggregate_curve(ds, demand_in_community, demand_out_community)
    user_id_to_bhattacharyya_distance = {}
    for user in all_users:
        dict2 = pad_dictionary(ds ,supply[user.user_id])
        user_id_to_bhattacharyya_distance[user.user_id] = bhattacharyya_distance(ds, dict1, dict2)

    # create the dictionary
    ranked_ids = list(sorted(user_id_to_bhattacharyya_distance,
                             key=lambda x: (user_id_to_bhattacharyya_distance[x], x),
                             reverse=False))
    return {id: ranked_ids.index(id) for id in ranked_ids}


def calculate_aggregate_curve(ds: ContentDemandSupply, 
                              demand_in_community: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]], 
                              demand_out_community: Dict[Union[UserType, int], DefaultDict[Any, Set[MinimalTweet]]]) \
                                -> Dict[Any, Set[MinimalTweet]]:
    """Helper function for calculate_bhattacharyya_ranks."""
    dict1 = pad_dictionary(ds, demand_in_community[UserType.CONSUMER])
    dict2 = pad_dictionary(ds, demand_in_community[UserType.CORE_NODE])
    for content_type in ds.content_space:
        dict1[content_type.representation] \
            = dict1[content_type.representation].union(dict2[content_type.representation])
    return dict1


def plot_tweet_count_over_time(ts_builder: SimpleTimeSeriesBuilder) -> None:
    """Creates a plot, where the x-axis is the time stamps specified by <ts_builder>, and the y-axis
    is the number of original tweets or the number of retweets in community."""
    original_tweets_list = ts_builder.partition_tweets_by_tweet_type("original_tweets")
    original_tweet_counts = [len(tweet_set) for tweet_set in original_tweets_list]
    retweets_in_community_list = ts_builder.partition_tweets_by_tweet_type("retweets_of_in_comm")
    retweet_in_community_counts = [len(tweet_set) for tweet_set in retweets_in_community_list]

    plt.plot(ts_builder.get_time_stamps(), original_tweet_counts, label="original tweets")
    plt.plot(ts_builder.get_time_stamps(), retweet_in_community_counts, label="retweets in community")
    plt.legend()
    plt.show()


def original_tweets_to_retweets_ratio(market: ContentMarket) -> None:
    """Prints the average ratio of the number of original tweets to the number of  retweets in 
    community for all users in <market>."""
    users = market.producers.union(market.consumers.union(market.core_nodes))
    ratios = []
    for user in users:
        if len(user.retweets_of_in_community) != 0:
            ratios.append(len(user.original_tweets) / (len(user.retweets_of_in_community)))
    print("Ratio of original tweets to retweets in community: " + str(sum(ratios) / len(ratios)))
