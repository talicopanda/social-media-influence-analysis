import pymongo

def ContentMarketMongoDAO(ContentMarketDAO):
    content_tweets_collection_name: str
    content_market_users_collection_name: str
    core_nodes_collection_name: str
    db_client: any # TODO: change this type and get pipenv working


    def __init__(self, config):
        self.content_tweets_collection_name = config.content_tweets_collection_name
        self.content_market_users_collection_name = config.content_market_users_collection_name
        self.core_nodes_collection_name = config.core_nodes_collection_name

        client = pymongo.MongoClient(config.connection_url)
        self.db = client[config.db_name]

    def load_tweet_content(self) -> List[ContentTweet]:
        pass

    def write_content_tweets(self, content_tweets: List[ContentTweet]):
        pass

    def load_content_market_users(self) -> List[ContentMarketUser]:
        pass

    def load_core_nodes(self) -> List[ContentMarketCoreNode]:
        pass

    def write_core_nodes(self, core_nodes: ContentMarketCoreNode) -> List[ContentMarketCoreNode]:
        pass

    def load_content_market(self) -> ContentMarket:
        pass



        

