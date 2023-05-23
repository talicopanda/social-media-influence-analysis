from Clustering.ContentMarketClustering import ContentMarketClustering

from typing import Dict, Any
import numpy as np


class EmbeddingClustering(ContentMarketClustering):

    embeddings: Dict[float, np.array]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        self.embeddings = args["embeddings"]

    def generate_tweet_to_type(self):
        self.tweet_to_type = {int(tweet_id): vector
                              for tweet_id, vector in self.embeddings.items()}
        print("===============Successfully Classify Content===============")
