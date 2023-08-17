from typing import Any


class ContentType:
    """A class that stores the content type information of a tweet.
    """
    # Attributes
    representation: Any

    def __init__(self, representation: Any) -> None:
        self.representation = representation

    def get_representation(self) -> Any:
        """Return <representation>.
        """
        return self.representation

    def set_representation(self, new_repr) -> None:
        """Set <representation> to <new_repr>.
        """
        self.representation = new_repr
