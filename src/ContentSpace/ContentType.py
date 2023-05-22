from typing import Any


class ContentType:
    # Attributes
    representation: Any

    def __init__(self, representation: Any) -> None:
        self.representation = representation

    def get_representation(self) -> Any:
        return self.representation

    def set_representation(self, new_repr) -> None:
        self.representation = new_repr
