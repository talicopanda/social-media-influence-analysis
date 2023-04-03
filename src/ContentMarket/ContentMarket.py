from typing import List, Tuple, Dict
from ContentMarket.ContentMarketConsumer import ContentMarketConsumer
from ContentMarket.ContentMarketProducer import ContentMarketProducer
from ContentMarket.ContentMarketCoreNode import ContentMarketCoreNode
from numpy import linalg
import numpy as np
import pickle
import datetime


class SupportEntry:
    """
    A class that stores info about a entry in a support function
    """

    def __init__(self, center, tweet_ids, furthest_tweet, furthest_tweet_dist, closest_tweet, closest_tweet_dist):
        self.center = center
        self.tweet_ids = tweet_ids
        self.furthest_tweet = furthest_tweet
        self.furthest_tweet_dist = furthest_tweet_dist
        self.closest_tweet = closest_tweet
        self.closest_tweet_dist = closest_tweet_dist


class ContentMarket:
    """
    A class that represents the a content market and calculates information about
    users/tweets demands, supplies and causations
    """

    consumers: List[ContentMarketConsumer]
    producers: List[ContentMarketProducer]
    core_nodes: List[ContentMarketCoreNode]
    computed_causations: List[float]

    def __init__(self, consumers, producers, core_nodes):
        self.consumers = consumers
        self.producers = producers
        self.core_nodes = core_nodes
        self.computed_causations = []

    # TODO: do we just decide the clusters here and let the users build their own support
    def build_support(embeddings: Dict[int, List], num_clusters: float) -> Dict[tuple, SupportEntry]:
        data = np.asarray(list(embeddings.values()), dtype=np.float32)
        ids = list(embeddings.keys())

        clusters, centers = kmer(data, num_clusters)

        assert(len(data) == len(ids) == len(clusters))

        support = {}
        for i in range(len(ids)):
            cluster_id = clusters[i]

            if cluster_id in support:
                entry = support[cluster_id]
                entry.tweet_ids.append(ids[i])

                dist_to_center = linalg.norm(data[i] - centers[cluster_id])
                if dist_to_center > entry.furthest_tweet_dist:
                    # update furthest tweet
                    entry.furthest_tweet = ids[i]
                    entry.furthest_tweet_dist = dist_to_center

                if dist_to_center < entry.closest_tweet_dist:
                    # update closest tweet
                    entry.closest_tweet = ids[i]
                    entry.closest_tweet_dist = dist_to_center
            else:
                support[cluster_id] = SupportEntry(
                    centers[cluster_id],
                    [ids[i]],
                    ids[i],
                    linalg.norm(data[i] - centers[cluster_id]),
                    ids[i],
                    linalg.norm(data[i] - centers[cluster_id]))

        # save support dictionary
        with open('../results/support.pickle', 'wb') as f:
            pickle.dump(support, f, protocol=pickle.HIGHEST_PROTOCOL)

        print(
            f"Unassigned vectors: {len(support[-1].tweet_ids)}")

        return support

    # def calulate_demand(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
    #     demand = 0
    #     for user_id in user_ids:
    #         user_tweets = get_tweets(user_id, time_range)  # db query
    #         for tweet in user_tweets:
    #             if tweet.type == TweetContent.TWEET and norm(tweet.content - content) < content_radius:
    #                 demand += 1
    #     return demand

    # def calculate_supply(self, content: TweetContent, content_radius: int, user_ids: List[str], time_range: Tuple(datetime)):
    #     supply = 0
    #     for user_id in user_ids:
    #         user_tweets = get_tweets(user_id, time_range)  # db query
    #         for tweet in user_tweets:
    #             if tweet.type == TweetContent.RETWEET and norm(tweet.content - content) < content_radius:
    #                 supply += 1
    #     return supply

    def calculate_causation(self):
        pass


def kmer(X: np.array, k: int, radius_tol=1e-3, max_iters=100) -> np.array:
    """
    We implement a modified version of the k-means algorithm, called the k-means with equal radius (KMER).
    The KMER algorithm modifies the traditional k-means algorithm by enforcing the radius constraint during the clustering process.

    The KMER algorithm is as follows:

    1. For a number of clusters k, initialize the cluster centers randomly.
    2. Calculate the distance between each vector and each cluster center.
    3. For each cluster, calculate the average distance from the cluster center to all the vectors assigned to the cluster.
    4. Find the maximum average distance among all the clusters, and set this distance as the desired radius for all the clusters.
    5. For each cluster, remove all vectors that are farther than the desired radius from the cluster center.
    6. Recalculate the cluster centers as the means of the remaining vectors assigned to each cluster.
    7. Repeat steps 2 to 6 until convergence (i.e., until the cluster centers do not change significantly).

    The function returns a tuple containing the final assignments and cluster centers.
    The assignments are an array of size n indicating the cluster index (0 to k-1) to which each vector is assigned.
    The centers are a matrix of shape (k, d) containing the coordinates of the cluster centers.
    """

    # Step 1: Initialize cluster centers randomly

    # np.random.choice generates an array of k unique integers between 0 and n-1,
    # which are used as indices to select the random vectors from X
    centers = X[np.random.choice(X.shape[0], k, replace=False), :]

    for iter in range(max_iters):

        # Computes the Euclidean distance between each vector in X and each cluster center in centers.
        # The resulting distances are stored in a two-dimensional array dists, where the i,j-th entry
        # contains the distance between the i-th vector in X and the j-th cluster center in centers.
        dists = np.linalg.norm(X[:, np.newaxis, :] - centers, axis=2)

        # Step 2: Assign each vector to the nearest cluster center
        assignments = np.argmin(dists, axis=1)

        # Step 3: Calculate average distance for each cluster
        avg_dists = np.zeros(k)
        for i in range(k):
            mask = (assignments == i)
            if np.sum(mask) > 0:  # if cluster i has a vector
                # calculates the average distance between the vectors assigned to i and the center of i
                avg_dists[i] = np.mean(np.linalg.norm(
                    X[mask, :] - centers[i], axis=1))

        # Step 4: Find the maximum average distance among all clusters
        max_avg_dist = np.max(avg_dists)

        # Step 5: Remove vectors that are farther than the desired radius from the cluster center
        for i in range(k):
            mask = (assignments == i)
            if np.sum(mask) > 0:  # if cluster i has a vector
                dists = np.linalg.norm(X[:, :] - centers[i], axis=1)
                dists[~mask] = np.nan
                keep_mask = (dists <= (max_avg_dist + radius_tol))
                assignments[mask & ~keep_mask] = -1

        # Step 6: Recalculate cluster centers as the means of the remaining vectors assigned to each cluster
        for i in range(k):
            mask = (assignments == i)
            if np.sum(mask) > 0:
                centers[i, :] = np.mean(X[mask, :], axis=0)

        # Step 7: Check for convergence
        if iter > 0 and np.all(assignments == old_assignments):
            break
        old_assignments = assignments.copy()

    # Return the final assignments and cluster centers
    return assignments, centers
