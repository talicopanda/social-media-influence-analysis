from typing import dict
import numpy as np
from enum import Enum


class EmbeddingType(Enum):
    TWEET2VEC = 1
    MEDIUM = 2
    WORD2VEC = 3


class ContentMarketEmbedding:
    """
    A class that manages a content embedding in a Content Market.

    A content embedding is a point in a 200-dimensional space that 
    represents the semantic value of the content string based on 
    tweet2vec's (https://arxiv.org/abs/1605.03481) implementation.
    """

    tweets_to_embedding: dict[int, np.array]

    def __init__(self, type: EmbeddingType):
        if type == EmbeddingType.TWEET2VEC:
            self.tweets_to_embedding = {}  # load
        elif type == EmbeddingType.MEDIUM:
            self.tweets_to_embedding = {}  # load
        elif type == EmbeddingType.WORD2VEC:
            self.tweets_to_embedding = {}  # load
        else:
            self.tweets_to_embedding = {}

    def get(id: int) -> np.array:
        if id in tweets_to_embedding:
            return tweets_to_embedding[id]
        return None
