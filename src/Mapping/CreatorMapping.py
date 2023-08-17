from Mapping.ContentTypeMapping import ContentTypeMapping
from DAO.ContentMarketMongoDAO import ContentMarketMongoDAO

from typing import Dict, Any, Optional


class CreatorMapping(ContentTypeMapping):
    """
    The representation of a ContentType is the original tweet's user_id.
    """

    dao: Optional[ContentMarketMongoDAO]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        self.dao = args["dao"]

    def generate_tweet_to_type(self) -> None:
        """Assign each tweet with its original tweet's creator.
        """
        content_type_set = set()
        # original tweets
        for tweet in self.dao.load_original_tweets():
            # extract information
            tweet_id = tweet.id
            user_id = tweet.user_id

            # store into class variable
            self.tweet_to_type[tweet_id] = self._populate_content_type(
                int(user_id), content_type_set)

        # retweets of in community
        for tweet in self.dao.load_retweets_of_in_community():
            # extract information
            tweet_id = tweet.id
            user_id = tweet.retweet_user_id

            # store into class variable
            self.tweet_to_type[tweet_id] = self._populate_content_type(
                int(user_id), content_type_set)

        # retweets of out community
        for tweet in self.dao.load_retweets_of_out_community():
            # extract information
            tweet_id = tweet.id
            user_id = tweet.retweet_user_id

            # store into class variable
            self.tweet_to_type[tweet_id] = self._populate_content_type(
                int(user_id), content_type_set)
        print("===============Successfully Classify Content===============")
        self.dao = None  # so that pickle.dump don't store this object
