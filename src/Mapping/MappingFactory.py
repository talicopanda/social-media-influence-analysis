from Mapping.ContentTypeMapping import ContentTypeMapping
from Mapping.CreatorMapping import CreatorMapping
from Mapping.KmersMapping import KmersMapping
from Mapping.EmbeddingMapping import EmbeddingMapping
from Mapping.BinningMapping import BinningMapping
from Mapping.WordsAnyMapping import WordsAnyMapping
from Mapping.WordVectorMapping import WordVectorMapping
from Mapping.WordsAllMapping import WordsAllMapping

from typing import Dict, Any


class MappingFactory:

    division_type: str

    def __init__(self, division_type: str):
        self.division_type = division_type

    def get_cluster(self, args: Dict[str, Any]) -> ContentTypeMapping:
        """Return ContentTypeMapping object by self.division_type.
        """
        try:
            if self.division_type == "kmers":
                return KmersMapping(args)
            elif self.division_type == "embedding":
                return EmbeddingMapping(args)
            elif self.division_type == "creator":
                return CreatorMapping(args)
            elif self.division_type == "binning":
                return BinningMapping(args)
            elif self.division_type == "word_any":
                return WordsAnyMapping(args)
            elif self.division_type == "word_vector":
                return WordVectorMapping(args)
            elif self.division_type == "word_all":
                return WordsAllMapping(args)
            else:
                raise ValueError
        except KeyError:
            print("args given doesn't match")
        except ValueError:
            print(f"invalid cluster type `{self.division_type}`")
        except:
            print("something else goes wrong")

    def to_cluster(self, mapping: Dict[int, Any]) -> CreatorMapping:
        content_type_set = set()
        creator = CreatorMapping({"dao": None})
        tweet_to_type = {}
        for tweet_id, type_repr in mapping.items():
            tweet_to_type[tweet_id] = creator._populate_content_type(
                type_repr, content_type_set)
        creator.tweet_to_type = tweet_to_type
        return creator

