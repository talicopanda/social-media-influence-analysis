from DAO.ContentMarketMongoDAO import ContentMarketMongoDAO
from DAO.ContentSpaceMongoDAO import ContentSpaceMongoDAO
from DAO.ContentDemandSupplyMongoDAO import ContentDemandSupplyMongoDAO

from typing import Dict


class DAOFactory:
    # TODO: may generalize the parameter
    def get_content_market_dao(self, db_config: Dict[str, str]) \
            -> ContentMarketMongoDAO:
        if db_config["db_type"] == "Mongo":
            return ContentMarketMongoDAO(**db_config)
        else:
            raise ValueError

    def get_content_space_dao(self, db_config: Dict[str, str]) \
            -> ContentSpaceMongoDAO:
        if db_config["db_type"] == "Mongo":
            return ContentSpaceMongoDAO(**db_config)
        else:
            raise ValueError

    def get_supply_demand_dao(self, db_config: Dict[str, str]) \
            -> ContentDemandSupplyMongoDAO:
        if db_config["db_type"] == "Mongo":
            return ContentDemandSupplyMongoDAO(**db_config)
        else:
            raise ValueError
