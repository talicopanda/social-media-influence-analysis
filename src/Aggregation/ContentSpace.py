from Mapping.ContentType import ContentType
from Mapping.ContentTypeMapping import ContentTypeMapping
from Aggregation.AggregationBase import AggregationBase
from User.ContentSpaceUser import ContentSpaceUser
from Tweet.ContentSpaceTweet import ContentSpaceTweet
from Tweet.TweetManager import TweetManager
from User.UserManager import UserManager

from typing import Set, Any


class ContentSpace(AggregationBase):
    # Attributes
    name: str
    consumers: Set[ContentSpaceUser]
    producers: Set[ContentSpaceUser]
    core_nodes: Set[ContentSpaceUser]

    original_tweets: Set[ContentSpaceTweet]
    retweets_of_in_comm: Set[ContentSpaceTweet]
    retweets_of_out_comm: Set[ContentSpaceTweet]
    # add retweets of out community by in community
    retweets_of_out_comm_by_in_comm: Set[ContentSpaceTweet]

    content_space: Set[ContentType]
    mapping: ContentTypeMapping

    def __init__(self, name, user_manager: UserManager,
                 tweet_manager: TweetManager):
        super().__init__(name, user_manager, tweet_manager)
        self._create_content_space_from_tweet()

    def _create_content_space_from_tweet(self) -> None:
        """Create a set of ContentType from ContentSpaceTweet and load into
        self.content_space.
        """
        content_space = []
        content_space.extend([tweet.content for tweet in self.original_tweets])
        content_space.extend([tweet.content for tweet in self.retweets_of_in_comm])
        content_space.extend([tweet.content for tweet in self.retweets_of_out_comm])
        # add retweets of out community by in community
        content_space.extend([tweet.content for tweet in self.retweets_of_out_comm_by_in_comm])
        self.content_space = set(content_space)

    def get_tweet_content_type_repr(self, tweet_id: int) -> Any:
        """Return ContentType for a Tweet with <tweet_id>.
        """
        return self.mapping.get_content_type(tweet_id).get_representation()

    def get_content_type(self, representation: Any) -> ContentType:
        """Return the ContentType object with <representation>.
        """
        # TODO: delete this or move to other place
        for content_type in self.content_space:
            if content_type.get_representation() == representation:
                return content_type
        raise KeyError(f"No ContentType has representation `{representation}`")

    def get_all_content_types(self) -> Set[ContentType]:
        """Return a set of all ContentType.
        """
        return self.content_space

    def set_content_type(self, tweet_id, representation: Any) -> None:
        """Change the belonging of the Tweet with <tweet_id> to ContentType
        with <representation>.
        """
        # TODO: delete this or move to other place
        for content_type in self.content_space:
            # Caution: if == does not work for some Objects,
            # so better to use primitive types as representation
            if content_type.get_representation() == representation:
                self.mapping.set_content_type(tweet_id, content_type)
                return
        raise ValueError(f"ContentType with `{representation}` does not exist")

    def get_all_user_ids(self) -> Set[int]:
        """Return a set of all user_ids.
        """
        all_users = self.producers | self.consumers | self.core_nodes
        return {user.user_id for user in all_users}

    def get_all_content_type_repr(self) -> Set[Any]:
        """Return a set of representation of all ContentType.
        """
        return {content_type.get_representation() for content_type
                in self.content_space}
