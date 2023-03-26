import json
import numpy as np
from typing import Dict, List, Any
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from numpy import linalg
import sys

DATA_PATH = "../results/"


""" 
Elbow method to find a good value of k:

A good model is one with low inertia AND a low number of clusters (K). 
However, this is a tradeoff because as K increases, inertia decreases.

See the graph outputted and find the k where the decrease in inertia begins to slow.
In other words, where the graph starts to platoe.
"""


def plot_kmeans_inertia(embeddings: Dict[int, List]):
    inertias = []

    min_k = 1
    max_k = len(embeddings) // 20  # 5% of data size to observe a trend

    print(
        f"Choosing best k value for kmeans in the range. Checking from k = {min_k} to k = {max_k}...")

    # https://stackoverflow.com/questions/835092/python-dictionary-are-keys-and-values-always-the-same-order
    data = list(embeddings.values())
    ids = list(embeddings.keys())
    print("k = ", end=' ')
    for i in range(min_k, max_k):
        print(i, end=' ')
        sys.stdout.flush()
        kmeans = KMeans(n_clusters=i, n_init="auto")
        kmeans.fit(data)
        inertia = kmeans.inertia_
        inertias.append(inertia)

    plt.plot(range(min_k, max_k), inertias, marker='o')
    plt.title('Elbow method')
    plt.xlabel('Number of clusters')
    plt.ylabel('Inertia')
    plt.show()
    print("Plot also saved under /experiments/kmeans_plot.png for convenience")
    plt.savefig("../experiments/kmeans_plot.png")


with open(DATA_PATH + "tweet2vec_embeddings.json") as f:
    embeddings = json.load(f)

    n = len(embeddings.values())

    # initialize with a value
    stats_per_axis = [{"mean": x / n, "min": x, "max": x}
                      for x in embeddings[list(embeddings.keys())[0]]]

    for e in embeddings.values():
        for i in range(len(e)):
            val = e[i]

            stats_per_axis[i]["mean"] += val / n
            if val < stats_per_axis[i]["min"]:
                stats_per_axis[i]["min"] = val
            if val > stats_per_axis[i]["max"]:
                stats_per_axis[i]["max"] = val

    print(f"Dimensions: {len(stats_per_axis)}")
    for i in range(len(stats_per_axis)):
        print(f"{i}: {stats_per_axis[i]}")

    min_range = np.inf
    max_range = -np.inf
    for stats in stats_per_axis:
        min_range = min(min_range, stats["min"])
        max_range = max(max_range, stats["max"])
    print(
        f"Min across dimensions: {min_range}, Max across dimensions: {max_range}")

    plot_kmeans_inertia(embeddings)
