from kmeans import kmer, plot_kmeans_inertia
import numpy as np
import json

DATA_PATH = "../results/"

# TODO: change to database DAO
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
