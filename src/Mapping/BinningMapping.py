from Mapping.ContentTypeMapping import ContentTypeMapping

from typing import Any, Dict

class BinningMapping(ContentTypeMapping):

    def __init__(self, args: Dict[str, Any]):
        super().__init__(args)
        
        embeddings = args["embeddings"]

    
    # def generate_tweet_to_type(self):
        