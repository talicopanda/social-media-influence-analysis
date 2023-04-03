from typing import Dict
import numpy as np


class ContentMarketClustering:

    tweet_to_cluster: Dict[int, int] # tweet id to cluster id
    cluster_centers: Dict[int, np.array] # cluster id to center vector
    radius: float

    def __init__(self, tweet_to_cluster, cluster_centers, radius):
        self.tweet_to_cluster = tweet_to_cluster
        self.cluster_centers = cluster_centers
        self.radius = radius

    def get_cluster_id(self, tweet_id):
        return self.tweet_to_cluster[tweet_id]
    
    def get_cluster_center(self, cluster_id):
        return self.cluster_centers[cluster_id]
