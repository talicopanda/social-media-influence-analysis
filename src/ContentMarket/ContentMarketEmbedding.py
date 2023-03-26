from typing import Dict
import numpy as np
from enum import Enum


class EmbeddingType(Enum):
    TWEET2VEC = 1
    MEDIUM = 2


class ContentMarketEmbedding:
    """
    A class that manages a content embedding in a Content Market.

    A content embedding is a point in a N-dimensional space that 
    represents the semantic value of the content string based on 
    tweet2vec's (https://arxiv.org/abs/1605.03481) implementation.
    """

    latent_space_dim: int
    embedding_type: EmbeddingType
    tweet_embeddings: Dict[int, np.array]  # maps id to embedding vector

    def __init__(self, type: EmbeddingType, tweet_embeddings: Dict[int, np.array]):
        if not tweet_embeddings.keys():
            raise Exception(
                "ContentMarketEmbedding: no tweet embedding in dictionary")

        self.tweet_embeddings = tweet_embeddings
        self.latent_space_dim = self._embedding_dim(tweet_embeddings)
        self.embedding_type = type

    """
    Ensures that all tweet embeddings are consitently with the same dimension
    and returns such dimension
    """
    def _embedding_dim(tweet_embeddings: Dict[int, np.array]) -> int:
        n = tweet_embeddings[tweet_embeddings.keys()[0]].size
        for val in tweet_embeddings.values():
            if n != val.size:
                raise Exception(
                    f'ContentMarketEmbedding: content embedding data is inconsistent. Expecting vector of dimension {n}, given {val.size}')
        return n

    def get(self, id: int) -> np.array:
        if id in self.tweet_embeddings:
            return self.tweet_embeddings[id]
        return None
