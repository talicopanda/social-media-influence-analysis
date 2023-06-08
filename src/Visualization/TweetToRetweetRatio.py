"""Contains all the functions related to finding the tweet to retweet user for different types of
users. """

from Aggregation.ContentDemandSupply import ContentDemandSupply
from User.UserType import UserType

from typing import Set
import matplotlib.pyplot as plt

def find_tweet_to_retweet_ratios(user_types: Set[UserType], mapping_manager: ContentDemandSupply,
                                 retweet_type: str):
    """Returns a list of ratios between tweets and retweets of <retweet_type> for all users of Type
    <user_type>

    <retweet_type> can take on one of three values -- in_community to find ratios for retweets
    in community only, out_community to find ratios for retweets out community only, and both to
    find ratios for all retweets.
    """
    users = set()
    for user_type in user_types:
        users = users.union(mapping_manager.user_manager.get_type_users(user_type))
    tweet_to_retweet_ratios = []
    for user in users:
        if retweet_type == "in_community":
            denominator = len(user.retweets_of_in_community)
        elif retweet_type == "out_community":
            denominator = len(user.retweets_of_out_community)
        elif retweet_type == "both":
            denominator = len(user.retweets_of_in_community) + len(user.retweets_of_out_community)
        else:
            raise Exception(f"Invalid retweet_type `{retweet_type}`")
        tweet_to_retweet_ratios.append(len(user.original_tweets) / denominator)
    return tweet_to_retweet_ratios

def plot_tweet_to_retweet_ratios(user_types: Set[UserType], mapping_manager: ContentDemandSupply,
                                 retweet_type: str, save: bool):
    tweet_to_retweet_ratios = find_tweet_to_retweet_ratios(user_types, mapping_manager, retweet_type)
    plt.figure()
    plt.hist(tweet_to_retweet_ratios, density=False)
    plt.title(" ".join(user_type.value for user_type in user_types) + " " + retweet_type)
    if save:
        plt.savefig(f'../results/tweet_to_retweet_ratios_' \
                    + "_".join(user_type.value for user_type in user_types) + "_" + retweet_type)
        plt.clf()

def calculate_mean_tweet_to_retweet_ratios(user_types: Set[UserType],
                                           mapping_manager: ContentDemandSupply,
                                           retweet_type: str):
    return sum(find_tweet_to_retweet_ratios(user_types, mapping_manager, retweet_type)) \
        / len(find_tweet_to_retweet_ratios(user_types, mapping_manager, retweet_type))
