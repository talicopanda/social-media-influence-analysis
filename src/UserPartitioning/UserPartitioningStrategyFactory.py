from UserPartitioning.UsersStrategy import UsersStrategy


def get_user_type_strategy(strategy: str):
    if strategy == "users":
        return UsersStrategy()
    else:
        raise ValueError(f"'{strategy}' does not exist")
