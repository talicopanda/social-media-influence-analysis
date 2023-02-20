# Table of Contents

- [Introduction](#introduction)
- [High-Level Organization](#high-level-organization)
- [Implementation](#implementation)
- [Influence](#causality)

# Introduction

In this project we aim to analyze content relationships in a network by calculating the amount of influence between any two agents.
For our purposes, an agent could be simply a single user or a set of users in a community.

More broadly, the goal of the project is to advance the understanding of social influence as a key feature of social media and a core mechanism underlying some of the main challenges emerging from the growing use of social media, including polarization, misinformation and disinformation, and the mental health crisis.
Specifically, we will test the hypothesis -- debated by sociological theorists but not empirically tested -- that social influence can be understood as a generalized (social) system of interchange, analogous to money or power.
Specifically, the project studies influence as a general system of interchange where attention and content are traded.

# High-Level Organization

In our code, we take a Object-Oriented Approach that is primarily reliant on the following classes:

## Tweet

A tweet object holds data about a tweet with respect to the user who tweeted, timestamp, etc.

It also holds the vector embedding representation of the tweet's content which is defined as a higher dimensional array in a latent space of content (see details in [Implementation](#implementation)).
Note that this tweet class allows for changes in the embedding algorithm in order to test the efficacy of multiple embedding approaches.

These tweets are stored in the `processed_influence_tweets` database.

## Community

A community object holds information about a specific community.

It contains and is defined by a list of users. Functionality includes processing all tweets from the community from the `raw_tweets` database to the `processed_influence_tweets`.

## Content Market

A content market is initialized with respect to a community and is used to manage and perform operations on the tweets within such community.
It also provides functions that calculate:

- **Demand** for a given content embedding, set of users and time range.
- **Supply** for a given content embedding, set of users and time range.
- **Causation** between any two values of demand or supply given a content embedding.

Refer to [this document](https://www.overleaf.com/6251411237wbdjqsjvrrjj) for a more detail mathematical definition of each function.

Values are computed on demand, output to the user, and stored in a `content_market` database. This has two purposes: 1) it allows values to be cached to reduce the time of future queries, and 2) It allows the `content_market` database to act as an output of our project, so that future research can populate certain content markets and then operate additional experiments using these content markets as input.

# Implementation

## High-Level OOP Diagram

![./Influence.drawio.png](./assets/influence_uml.png)

## Latent Space Embedding

We rely on previous literate for latent space embedding of our model, namely [tweet2vec](https://arxiv.org/abs/1605.03481).
For starters, this approach assumes that posts with the same hashtags should have embeddings which are close to each other.
Hence, the authors train a Bi-directional Gated Recurrent Unit (Bi-GRU) neural network with the training objective of predicting hashtags for a post from its latent representation in order to verify latent representation correctness.

The dataset used for training the model consists of over 2 million global tweets in English between the dates of June 1, 2013 to June 5, 2013 with at least one hashtag.
This could potentially impose a bias in the data where the model only performs differently on posts without hashtags.
As such, we allow our program to easily integrated other embeding techniques for comparison.

## Data Ingestion

Previous work done in [SNACES/core](https://github.com/SNACES/core) will be leveraged for data ingestion. Primarily, the logic to download tweets for a user or community, as well as to find communities based off an input user, will be used in the pipeline to generate all the needed inputs to the above components.

# Causality

To infer causality between supply and demand between core-periphery nodes, we use time series data to capture the information, and use granger causality to infer if there is any relationship between the time series. We use [this library](https://www.statsmodels.org/dev/generated/statsmodels.tsa.stattools.grangercausalitytests.html) to implement the granger causality function. 

# Issues

Twitter API has readjusted pricing model -> new basic tier will cost $100/month
