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
        """generate tweet to Content Type representation mapping, and store the
        results in self.tweet_to_type.
        """
        raise NotImplementedError

    def get_content_type(self, tweet_id: int) -> ContentType:
        """Return the ContentType object that the Tweet with <tweet_id> mapped
        to in self.tweet_to_type.
        """
        return self.tweet_to_type[tweet_id]

    def set_content_type(self, tweet_id: int, new_type: ContentType):
        """Set the mapped value of Tweet with <tweet_id> to <new_type>.
        """
        self.tweet_to_type[tweet_id] = new_type

    def get_all_content_type(self) -> Set[ContentType]:
        """Return a set of all ContentType objects getting mapped to.
        """
        return set(self.tweet_to_type.values())

    def _populate_content_type(self, representation: Any,
                               content_type_set: Set[ContentType]) \
            -> ContentType:
        """A helper function returning the ContentType with <representation>.
        If there also exists such ContentType in <content_type_set>, return it;
        else create a new ContentType with <representation>, store in
        <content_type_set>, and return the new one.
        """
        for content_type in content_type_set:
            if content_type.representation == representation:
                # this means that such ContentType has been created,
                # so return the object
                return content_type

        # else create the content type and return the new object
        new_type = ContentType(representation)
        content_type_set.add(new_type)
        return new_type

