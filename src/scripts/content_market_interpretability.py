import numpy as np
from numpy import linalg
from kmeans import kmer
import json
from ContentMarket.ContentMarketSupportEntry import ContentMarketSupportEntry

DATA_PATH = "../results/"
num_clusters = 20

# open(DATA_PATH + "tweet2vec_text.json") as f3:
with open(DATA_PATH + "tweet2vec_embeddings.json") as f1, open(DATA_PATH + "tweet2vec_hashtags.json") as f2:
    embeddings = json.load(f1)
    hashtags = json.load(f2)
    # text = json.load(f3)

    data = np.asarray(list(embeddings.values()), dtype=np.float32)
    ids = list(embeddings.keys())

    clusters, centers, _, _ = kmer(data, num_clusters)

    assert(len(data) == len(ids) == len(clusters))

    support = {}
    for i in range(len(ids)):
        cluster_id = clusters[i]

        if cluster_id in support:
            entry = support[cluster_id]
            entry.tweet_ids.append(ids[i])

            dist_to_center = linalg.norm(data[i] - centers[cluster_id])
            if dist_to_center > entry.furthest_tweet_dist:
                # update furthest tweet
                entry.furthest_tweet = ids[i]
                entry.furthest_tweet_dist = dist_to_center

            if dist_to_center < entry.closest_tweet_dist:
                # update closest tweet
                entry.closest_tweet = ids[i]
                entry.closest_tweet_dist = dist_to_center
        else:
            support[cluster_id] = ContentMarketSupportEntry(
                centers[cluster_id],
                [ids[i]],
                ids[i],
                linalg.norm(data[i] - centers[cluster_id]),
                ids[i],
                linalg.norm(data[i] - centers[cluster_id]))

    for c in support:
        entry = support[c]
        modes = {}
        for id in entry.tweet_ids:
            for hashtag in hashtags[id].split(" "):
                if hashtag in modes:
                    modes[hashtag] += 1
                else:
                    modes[hashtag] = 1

        print(f"=== Cluster id: {c} ===")
        top5 = [(k, v) for k, v in sorted(
            modes.items(), key=lambda item: item[1], reverse=True)][:5]
        print(f"Top 5 Themes (out of {len(entry.tweet_ids)} items): ", end=" ")
        for x in top5:
            print(f"{x[0]} ({x[1]}), ", end=" ")
        print()

        print("If the following two tweets are related to each other around the same topic, the clustering is likely to be a good one:")
        print(
            f"Tweet closest to center ('represents' the content the most): {hashtags[entry.closest_tweet]} (dist: {entry.closest_tweet_dist})")
        print(
            f"Tweet furthest to center ('represents' the content the least): {hashtags[entry.furthest_tweet]} (dist: {entry.furthest_tweet_dist})")
