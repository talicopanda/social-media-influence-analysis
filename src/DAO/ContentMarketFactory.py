from ContentMarketMongoDAO import ContentMarketMongoDAO

class ContentMarketFactory:
    def get_content_market_dao(db_type, config):
        if db_type == "Mongo":
            return ContentMarketMongoDAO(config)
        else:
            ValueError