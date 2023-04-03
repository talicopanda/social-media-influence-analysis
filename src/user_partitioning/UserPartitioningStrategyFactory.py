from user_partitioning.UsersStrategy import UsersStrategy

class UserPartitioningStrategyFactory:
    def get_user_type_strategy(strategy: str):
        if strategy == "users":
            return UsersStrategy()
        else:
            ValueError