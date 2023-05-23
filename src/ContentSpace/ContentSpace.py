from ContentSpace.ContentType import ContentType
from Clustering.ContentMarketClustering import ContentMarketClustering
from typing import Set, Any


class ContentSpace:
    # Attributes
    content_space: Set[ContentType]
    clustering: ContentMarketClustering

    def create_content_space(self, clustering: ContentMarketClustering) -> None:
        """Set value for <content_space> and <clustering>. If the clustering is
        not valid, i.e. it's ContentType contains duplicate representation, then
        there will raise Exception.
        """
        print("=================Start Creating=================")
        self.content_space = set()
        repr_list = []
        for content_type in clustering.get_all_content_type():
            new_repr = content_type.get_representation()
            if new_repr not in repr_list:
                self.content_space.add(content_type)
            else:
                self.content_space.clear()
                raise Exception(f"Duplicate Representation in "
                                f"Content Type `{new_repr}`")
        self.clustering = clustering
        print("=============Successfully Build Content Space=============")

    def get_content_type(self, tweet_id: int) -> ContentType:
        """Return ContentType for a Tweet with <tweet_id>.
        """
        return self.clustering.get_content_type(tweet_id)

    def set_content_type(self, tweet_id, representation: Any) -> None:
        """Change the belonging of the Tweet with <tweet_id> to ContentType
        with <representation>.
        """
        for content_type in self.content_space:
            # Caution: if == does not work for some Objects,
            # so better to use primitive types as representation
            if content_type.get_representation() == representation:
                self.clustering.set_content_type(tweet_id, content_type)
                return

    def set_group_content_type(self, tweet_id, new_representation: Any) -> None:
        """Change the ContentType's representation for all Tweets which belongs
        to the same ContentType as <tweet_id>.
        """
        self.get_content_type(tweet_id).set_representation(new_representation)
