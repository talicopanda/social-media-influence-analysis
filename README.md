# Table of Contents

- [Introduction](#introduction)
- [High-Level Organization](#high-level-organization)
- [Implementation](#implementation)

# Introduction

In this project we aim to analyze content relationships in a network by calculating a value representing the amount of influence between any two agents.
For our purposes, an agent could be simply a single user or a set of users in a community.

More broadly, the goal of the project is to advance the understanding of social influence as a key feature of social media and a core mechanism underlying some of the main challenges emerging from the growing use of social media, including polarization, misinformation and disinformation, and the mental health crisis.
Specifically, we will test the hypothesis -- debated by sociological theorists but not empirically tested -- that social influence can be understood as a generalized (social) system of interchange, analogous to money or power.
Specifically, the project studies influence as a general system of interchange where attention and content are traded.

# High-Level Organization

In our code, we take a Object-Oriented Approach that is primarily reliant on the following classes:

## Tweet

A tweet object holds data about a tweet with respect to the following information:

- id
- timestamp: timestamp of tweet
- user: user who tweeted
- num_retweets: number of retweets
- likes: number of likes
- retweets: retweets of this tweet as an array of tweet ids

It also holds a reference to the embedding representation of the tweet's content which is defined as a higher dimensional array in a latent space of content (see details in [Implementation](#implementation)).

These tweets are stored in the `processed_influence_tweets` database.
Moreover, the content embeddings are stored in a separate database to allow for effortless changes in the embedding algorithm as well as testing the efficacy of different embedding approaches.

## User

Fields:

- id
- followers: users that follow this user
- following: users that this user is following
- tweets
- retweets
- retweets in community: the retweets of this user's tweets or retweets by users that follow this user and with a post time after the corresponding tweet/retweet of this user (check who retweeted my retweet/tweet based on the timestamp and if the user follows me).

## Community

A community object holds information about a specific community.

- core nodes: the set of detected core nodes in a community
- users: array of all users pbjects in a community

It contains and is defined by a list of users.
Functionality includes processing all tweets from the community from the `raw_tweets` database to the `processed_influence_tweets`.

## Content Market

A content market is initialized with respect to a community and is used to manage and perform operations on the tweets within such community.
It holds information about:

- community: the community object for this content market

It provides functions that calculate:

- **Demand** for a given content embedding, set of users and time range as defined as following:
  ![./demand.jpg](./assets/demand.jpg)
- **Supply** for a given content embedding, set of users and time range as defined as following:
  ![./supply.jpg](./assets/supply.jpg)
- **Causation** between any two values of demand or supply given a content embedding as defined as following:
  ![./causality1.jpg](./assets/causality1.jpg)
  ![./causality2.jpg](./assets/causality2.jpg)

Refer to [this document](https://www.overleaf.com/6251411237wbdjqsjvrrjj) for more context on these definitions.

Values are computed on demand, output to the user, and stored in a `content_market` database. This has two purposes: 1) it allows values to be cached to reduce the time of future queries, and 2) It allows the `content_market` database to act as an output of our project, so that future research can populate certain content markets and then operate additional experiments using these content markets as input.

## DAO

For each of the above objects, we have a corresponding DAO object. This DAO objects acts as an interface with MongoDB, allowing us to seperate the database accesses with our high level object definitions, giving us resiliciency to data definition changes and seperating database accesses from the responsbility of our objects. These DAO objects have load and write functions.

# Implementation

## High-Level OOP Diagram TODODODODODO

![./Influence.drawio.png](./assets/influence_uml.png)

## Latent Space Embedding

We rely on previous literate for latent space embedding of our model, namely [tweet2vec](https://arxiv.org/abs/1605.03481).
For starters, this approach assumes that posts with the same hashtags should have embeddings which are close to each other.
Hence, the authors train a Bi-directional Gated Recurrent Unit (Bi-GRU) neural network with the training objective of predicting hashtags for a post from its latent representation in order to verify latent representation correctness.

The dataset used for training the model consists of over 2 million global tweets in English between the dates of June 1, 2013 to June 5, 2013 with at least one hashtag.
This could impose a bias in the data where the model performs differently on posts without hashtags.
As such, we allow our program to easily integrated other embedding techniques for comparison.

We thus consider trying two further approaches:

1. Averaging the word embedding vectors of every word in a tweet
2. Training a new tweet2vec encodder based strictly on our community's tweets

### Demand / Supply Functions

The supply and demand functions are represented as a hashtable that maps a tuple of size n to its respective quantity of demand/supply, where n is the dimension of the latent space. An n-tuple corresponds to a 'bin' or space in $R^n$, which are equal in size and aligned on non-overlapping intervals (for example, bin 1 may be a hypercube of size 1 centered at the zero vector, bin 2 a hypercube of size 1 centered at the $\vec{1}$, and so on until all tweets are encompassed within a hypercube).
We have a utility function which maps a given content vector to key / n-tuple that corresponds to the bin containing the vector. The support of the function is the keys in the hashtable, as only bins with non-zero demand or supply are keys.

## Causality

To infer causality (influence) between supply and demand between core-periphery nodes, we use time series data to capture the information, and use granger causality to infer if there is any relationship between the time series. We use [this module](https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.grangercausalitytests.html) to implement the granger causality function.

# Issues

Twitter API has readjusted pricing model -> new basic tier will cost $100/month
