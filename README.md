# Table of Contents

- [Introduction](#introduction)
- [High-Level Organization](#high-level-organization)
- [Implementation](#implementation)

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

## Community

A community object holds information about a specific community.

TODO: what else will "Community hold"

## Content Market

A content market is initialized with respect to a community and is used to manage the tweets within such community.
It also provides functions that calculate:

- **Demand** for a given content embedding, set of users and time range.
- **Supply** for a given content embedding, set of users and time range.
- **Causation** between any two values of demand or supply given a content embedding.

Refer to [this document](https://www.overleaf.com/6251411237wbdjqsjvrrjj) for a more detail mathematical definition of each function.

# Implementation

## Latent Space Embedding

We rely on previous literate for latent space embedding of our model, namely [tweet2vec](https://arxiv.org/abs/1605.03481).
For starters, this approach assumes that posts with the same hashtags should have embeddings which are close to each other.
Hence, the authors train a Bi-directional Gated Recurrent Unit (Bi-GRU) neural network with the training objective of predicting hashtags for a post from its latent representation in order to verify latent representation correctness.

The dataset used for training the model consists of over 2 million global tweets in English between the dates of June 1, 2013 to June 5, 2013 with at least one hashtag.
This could potentially impose a bias in the data where the model only performs differently on posts without hashtags.
As such, we allow our program to easily integrated other embeding techniques for comparison.

TODO: details of database accesses, ingestion and any non-trivial implementation details

# Workflow

1. Download and setup SNACES/core according to its documentation
2. Run 'Process Tweets' with the -vectorize option enabled to add word embedding vectors to processed tweets
3. Run ./SNACES.py, select Influence, then choose which functionality and give input as prompted.

There will be 3 main categories of functionality:

1. Graphing

- Graph a given user's demand curve
- Graph a given user's supply curve
- Graph a given communities's supply curve
- Graph a given communities's supply curve

2. Correlation

- Graph a two user's, one user and one community, or two communities', calculate correlation between either demand or supply curves

3. Causation

- Graph a two user's, one user and one community, or two communities', calculate causation between either demand or supply curves

Note that for passing in communities or influencer's, the user can input only the required information to find a community / influencer, and they will be found programatically by leveraging SNACES functionality.

# Plan:

Fork SNACES repo

- Change certain definitions, i.e processed tweet, to add processing on ingestion that matches our use cases as we want vectorized definitions on tweets
- Add functionality to SNACES.py that guides / gathers user input
- Call SNACES functionality (DetectCoreActivity, run_clustering) to compute required objects
- Run corresponding functionality defined in this repository with computed inputs
- Output to user or to database as directed by input

# Issues

Twitter API has readjusted pricing model -> new basic tier will cost $100/month
