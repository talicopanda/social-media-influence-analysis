from UserPartitioning.UsersStrategy import UsersStrategy


class UserPartitioningStrategyFactory:
    def get_user_type_strategy(self, strategy: str):
        if strategy == "users":
            return UsersStrategy()
        else:
            raise ValueError(f"'{strategy}' does not exist.")
