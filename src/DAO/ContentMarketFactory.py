from ContentMarketMongoDAO import ContentMarketMongoDAO

class ContentMarketFactory:
    def get_content_market_dao(db_config):
        if db_config['db_type'] == "Mongo":
            return ContentMarketMongoDAO(db_config['db_name'], db_config['users_collection'], db_config['tweet_content_collection'])
        else:
            ValueError