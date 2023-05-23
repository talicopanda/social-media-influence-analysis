from abc import ABC, abstractmethod
from ContentSpace.ContentType import ContentType

from typing import Dict, Any, Set


class ContentMarketClustering(ABC):

    tweet_to_type: Dict[int, ContentType]  # tweet id to ContentType

    @abstractmethod
    def __init__(self, args: Dict[str, Any]):
        print("=================Classify Content=================")
        self.tweet_to_type = {}

    @abstractmethod
    def generate_tweet_to_type(self):
        raise NotImplementedError

    def get_content_type(self, tweet_id: int) -> ContentType:
        return self.tweet_to_type[tweet_id]

    def set_content_type(self, tweet_id: int, new_type: ContentType):
        self.tweet_to_type[tweet_id] = new_type

    def get_all_content_type(self) -> Set[ContentType]:
        """Return a set of ContentType objects
        """
        return set(self.tweet_to_type.values())

    def _populate_content_type(self, representation: Any,
                               content_type_set: Set[ContentType]) \
            -> ContentType:
        for content_type in content_type_set:
            if content_type.representation == representation:
                # this means that such ContentType has been created,
                # so return the object
                return content_type

        # else create the content type and return the new object
        new_type = ContentType(representation)
        content_type_set.add(new_type)
        return new_type

