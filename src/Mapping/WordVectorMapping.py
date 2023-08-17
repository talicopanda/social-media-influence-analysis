from Mapping.ContentTypeMapping import ContentTypeMapping
from DAO.ContentMarketMongoDAO import ContentMarketMongoDAO

from typing import Dict, Any, Optional, List, Tuple


class WordVectorMapping(ContentTypeMapping):
    """
    The representation of a ContentType is a vector of 0 or 1 that indicates
    whether the content of the tweet contains such words.
    """

    dao: Optional[ContentMarketMongoDAO]
    words: List[str]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        self.dao = args["dao"]
        self.words = args["words"]

    def generate_tweet_to_type(self) -> None:
        """A tweet has a vector of 0's and 1's indicating whether its content
        have such word or not.
        """
        content_type_set = set()
        # original tweets
        for tweet in self.dao.load_original_tweets():
            self.tweet_to_type[tweet.id] = self._populate_content_type(
                self._create_vector(tweet.content), content_type_set
            )

        # retweets of in community
        for tweet in self.dao.load_retweets_of_in_community():
            self.tweet_to_type[tweet.id] = self._populate_content_type(
                self._create_vector(tweet.content), content_type_set
            )

        # retweets of out community
        for tweet in self.dao.load_retweets_of_out_community():
            self.tweet_to_type[tweet.id] = self._populate_content_type(
                self._create_vector(tweet.content), content_type_set
            )
        print("===============Successfully Classify Content===============")
        self.dao = None  # so that pickle.dump don't store this object

    def _create_vector(self, text: str) -> Tuple[int]:
        """Return 1 if <text> contains at least one word in <self.words>,
        return 0 if it doesn't.
        """
        vector = []
        for word in self.words:
            if word in text:
                vector.append(1)
            else:
                vector.append(0)
        return tuple(vector)
