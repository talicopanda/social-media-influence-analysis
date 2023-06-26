from UserPartitioning.UsersStrategy import UsersStrategy
from UserPartitioning.SocialSupportStrategy import SocialSupportStrategy


def get_user_type_strategy(strategy: str):
    if strategy == "users":
        return UsersStrategy()
    if strategy == "social_support":
        return SocialSupportStrategy()
    else:
        raise ValueError(f"'{strategy}' does not exist")
