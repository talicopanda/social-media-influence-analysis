from Clustering.ContentMarketClustering import ContentMarketClustering
from Clustering.CreatorClustering import CreatorClustering
from Clustering.KmersClustering import KmersClustering
from typing import Dict, Any


class ContentMarketClusteringFactory:

    division_type: str

    def __init__(self, division_type: str):
        self.division_type = division_type

    def get_cluster(self, args: Dict[str, Any]) -> ContentMarketClustering:
        try:
            if self.division_type == "kmers":
                return KmersClustering(args)
            elif self.division_type == "creator":
                return CreatorClustering(args)
            else:
                raise ValueError
        except KeyError:
            print("args given doesn't match")
        except ValueError:
            print(f"invalid cluster type `{self.division_type}`")
        except:
            print("something else goes wrong")
