from Clustering.ContentMarketClustering import ContentMarketClustering
from DAO.ContentMarketDAO import ContentMarketDAO

from typing import Dict, Any, Optional


class CreatorClustering(ContentMarketClustering):

    dao: Optional[ContentMarketDAO]

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        self.dao = args["dao"]

    def generate_tweet_to_type(self):
        """Assign each tweet with its original tweet's creator.
        """
        content_type_set = set()
        for tweet_group in [self.dao.load_original_tweets(),
                            self.dao.load_quotes_of_in_community(),
                            self.dao.load_quotes_of_out_community(),
                            self.dao.load_retweets_of_in_community(),
                            self.dao.load_retweets_of_out_community()]:
            for tweet in tweet_group:
                # extract information
                tweet_id = tweet["id"]
                user_id = tweet["user_id"]

                # store into class variable
                self.tweet_to_type[tweet_id] = self._populate_content_type(
                    int(user_id), content_type_set)
        print("===============Successfully Classify Content===============")
        self.dao = None # so that pickle.dump can store this object
