from ContentMarketMongoDAO import ContentMarketMongoDAO

class ContentMarketFactory:
    def get_content_market_dao(db_type, db_name, users_collection_name, tweet_embeddings_collection_name):
        if db_type == "Mongo":
            return ContentMarketMongoDAO(db_name, users_collection_name, tweet_embeddings_collection_name)
        else:
            ValueError