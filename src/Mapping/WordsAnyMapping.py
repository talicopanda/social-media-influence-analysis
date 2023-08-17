from Mapping.ContentTypeMapping import ContentTypeMapping
from DAO.ContentMarketMongoDAO import ContentMarketMongoDAO

from typing import Dict, Any, Optional, List


class WordsAnyMapping(ContentTypeMapping):
    """
    The representation of the ContentType is 1 if it contains at least one
    of the word in <words>.
    """

    dao: Optional[ContentMarketMongoDAO]
    words: List[str]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        self.dao = args["dao"]
        self.words = args["words"]

    def generate_tweet_to_type(self) -> None:
        """A tweet has type 1 if it contains any of the words in self.words.
        """
        content_type_set = set()
        # original tweets
        for tweet in self.dao.load_original_tweets():
            self.tweet_to_type[tweet.id] = self._populate_content_type(
                self._contains_word(tweet.content), content_type_set
            )

        # retweets of in community
        for tweet in self.dao.load_retweets_of_in_community():
            self.tweet_to_type[tweet.id] = self._populate_content_type(
                self._contains_word(tweet.content), content_type_set
            )

        # retweets of out community
        for tweet in self.dao.load_retweets_of_out_community():
            self.tweet_to_type[tweet.id] = self._populate_content_type(
                self._contains_word(tweet.content), content_type_set
            )
        print("===============Successfully Classify Content===============")
        self.dao = None  # so that pickle.dump don't store this object

    def _contains_word(self, text: str) -> int:
        """Return 1 if <text> contains at least one word in <self.words>,
        return 0 if it doesn't.
        """
        for word in self.words:
            if word in text:
                return 1
        return 0
