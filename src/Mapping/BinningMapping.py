from Mapping.ContentTypeMapping import ContentTypeMapping
from Aggregation.ContentMarket import ContentMarket

from typing import Any, Dict, List, Optional
import numpy as np
from sklearn.decomposition import PCA


class BinningMapping(ContentTypeMapping):
    """
    The representation of a ContentType is determined by 1D PCA.
    """

    ids: List[int]
    market: Optional[ContentMarket]
    bin_boundaries: List[float]
    bins: List[int]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)

        ### Unfiltered #############################################################################
        embeddings = args["embeddings"]
        num_bins = args["num_bins"]

        # PCA onto one dimension
        X = np.asarray(list(embeddings.values()), dtype=np.float32)

        self.ids = list(embeddings.keys())

        pca = PCA(n_components=1)
        pca.fit(np.transpose(np.asarray(X)))

        min_pca, max_pca = min(pca.components_[0]), max(pca.components_[0])
        bin_size = (max_pca - min_pca) / num_bins

        self.bin_boundaries = [min_pca + i * bin_size for i in range(num_bins - 1)] + [max_pca]

        self.bins = [self._find_bin_number(pca_value) for pca_value in pca.components_[0]]

        ### Filtered (uncomment below) ############################################################
        # embeddings = args["embeddings"]
        # num_bins = args["num_bins"]

        # self.market = args["market"]

        # original_tweet_ids = {tweet.id for tweet in self.market.original_tweets}
        # retweets_of_in_comm_ids = {tweet.id for tweet in self.market.retweets_of_in_comm}
        # retweets_of_out_comm_ids = {tweet.id for tweet in self.market.retweets_of_out_comm}
        # retweets_of_out_comm_by_in_comm_ids = {tweet.id for tweet in self.market.retweets_of_out_comm_by_in_comm}
        # # all_ids = original_tweet_ids.union(retweets_of_in_comm_ids.union(retweets_of_out_comm_ids.union(retweets_of_out_comm_by_in_comm_ids)))
        # all_ids = original_tweet_ids.union(retweets_of_in_comm_ids)

        # new_embeddings = {}
        # for tweet_id in embeddings:
        #     if tweet_id in all_ids:
        #         new_embeddings[tweet_id] = embeddings[tweet_id]

        # # PCA onto one dimension
        # X = np.asarray(list(new_embeddings.values()), dtype=np.float32)
        # print(len(X))

        # self.ids = list(new_embeddings.keys())

        # pca = PCA(n_components=1)
        # pca.fit(np.transpose(np.asarray(X)))

        # min_pca, max_pca = min(pca.components_[0]), max(pca.components_[0])
        # bin_size = (max_pca - min_pca) / num_bins

        # self.bin_boundaries = [min_pca + i * bin_size for i in range(num_bins - 1)] + [max_pca]

        # self.bins = [self._find_bin_number(pca_value) for pca_value in pca.components_[0]]


    def generate_tweet_to_type(self) -> None:
        """Assign each tweet with a bin."""
        content_type_set = set()
        for i in range(len(self.ids)):
            bin_number = self.bins[i]
            self.tweet_to_type[int(self.ids[i])] = self._populate_content_type(
                bin_number, content_type_set)
        print("===============Successfully Classify Content===============")

    def _find_bin_number(self, num):
        """Find which bin the value belongs in.
        Note: this could be more efficient if we used binary search."""
        for i in range(len(self.bin_boundaries)):
            if num < self.bin_boundaries[i]:
                return i - 1
        return len(self.bin_boundaries) - 1

