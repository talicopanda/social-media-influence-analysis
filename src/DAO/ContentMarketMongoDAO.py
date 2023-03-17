def ContentMarketMongoDAO(ContentMarketDAO):
    content_tweets_collection_name: str
    content_market_users_collection_name: str
    core_nodes_collection_name: str
    db_client: any # TODO: change this type and get pipenv working


    def __init__(self, config):
        self.content_tweets_collection_name = config.content_tweets_collection_name
        self.content_market_users_collection_name = config.content_market_users_collection_name
        self.core_nodes_collection_name = config.core_nodes_collection_name

        client = MongoClient(config.connection_url)
        self.db = client[config.db_name]

    def load_content_tweets(self) -> List[ContentTweet]:
        # tweets_collection = self.db_client[self.content_tweets_collection_name]
        # tweets_collection.find()

    @abstractmethod
    def load_content_market_users(self) -> List[ContentMarketUser]:
        pass

    @abstractmethod
    def load_core_nodes(self) -> List[ContentMarketCoreNode]:
        pass

    @abstractmethod
    def load_content_market(self) -> ContentMarket:
        pass

        

