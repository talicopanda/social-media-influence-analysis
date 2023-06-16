from Mapping.ContentTypeMapping import ContentTypeMapping

import numpy as np
from typing import Dict, Any, List, Tuple


class KmersMapping(ContentTypeMapping):

    cluster_centers: Dict[str, np.array]  # cluster id to center vector
    radius: float
    ids: List[int]
    clusters: np.array
    centers: np.array

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        embeddings = args["embeddings"]
        num_clusters = args["num_clusters"]

        # save useful data for generate_tweet_to_cluster
        data = np.asarray(list(embeddings.values()), dtype=np.float32)
        clusters, centers, radius = kmer(data, num_clusters)

        ids = list(embeddings.keys())

        assert (len(data) == len(ids) == len(clusters))

        self.ids = ids
        self.clusters = clusters
        self.centers = centers
        self.radius = radius

    def generate_tweet_to_type(self):
        """Assign each tweet with cluster generated from Kmers algorithm.
        """
        content_type_set = set()
        for i in range(len(self.ids)):
            cluster_id = self.clusters[i]
            self.tweet_to_type[int(self.ids[i])] = self._populate_content_type(
                int(cluster_id), content_type_set)

        self.cluster_centers = {}
        for i in range(len(self.centers)):
            self.cluster_centers[str(i)] = self.centers[i].tolist()
        print("===============Successfully Classify Content===============")

    def get_cluster_center(self, cluster_id):
        return self.cluster_centers[str(cluster_id)]


def kmer(X: np.array, k: int, radius_tol=0.1, max_iters=100) \
        -> Tuple[np.array, np.array, float]:
    """
    We implement a modified version of the k-means algorithm, called the k-means with equal radius (KMER).
    The KMER algorithm modifies the traditional k-means algorithm by enforcing the radius constraint during the mapping process.

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
    # Seed to ensure consistency between different files
    np.random.seed(42)

    # Step 1: Initialize cluster centers randomly

    # np.random.choice generates an array of k unique integers between 0 and n-1,
    # which are used as indices to select the random vectors from X
    centers = X[np.random.choice(X.shape[0], k, replace=False), :]
    radius = 0
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
            radius = max_avg_dist
            break
        old_assignments = assignments.copy()

    return assignments, centers, radius
