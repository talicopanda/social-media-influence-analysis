from Mapping.ContentTypeMapping import ContentTypeMapping

import numpy as np
from kmeans import kmer
from typing import Dict, Any, List


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

