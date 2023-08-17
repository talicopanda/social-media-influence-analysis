from Mapping.ContentTypeMapping import ContentTypeMapping

from typing import Dict, Any


class DictMapping(ContentTypeMapping):
    """
    directly pass in tweet_to_type.
    """

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        # extract arguments
        self.tweet_to_type = args["tweet_to_type"]

    def generate_tweet_to_type(self) -> None:
        pass
