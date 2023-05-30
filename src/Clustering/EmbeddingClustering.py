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
        """Assign each tweet with embedding vector generated from ./tweet2vec.
        """
        content_type_set = set()
        for tweet_id, vector in self.embeddings.items():
            self.tweet_to_type[tweet_id] = self._populate_content_type(
                tuple(vector), content_type_set)

        print("===============Successfully Classify Content===============")
