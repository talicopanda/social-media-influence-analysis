from Mapping.ContentTypeMapping import ContentTypeMapping

from typing import Any, Dict, List
import numpy as np
from sklearn.decomposition import PCA


class BinningMapping(ContentTypeMapping):

    ids: List[int]
    bin_boundaries: List[float]
    bins: List[int]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)

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

    def generate_tweet_to_type(self):
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

