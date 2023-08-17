from DAO.DAOFactory import DAOFactory
from UserPartitioning import UserPartitioningStrategyFactory
from Builder.ContentMarketBuilder import ContentMarketBuilder
from Tweet.ContentMarketTweet import ContentMarketTweet

import json
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation, MiniBatchNMF
import matplotlib.pyplot as plt
from typing import Set, List, Tuple
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from gensim.models.coherencemodel import CoherenceModel
from gensim.corpora.dictionary import Dictionary
from gensim.models.nmf import Nmf
import numpy as np
from operator import itemgetter
import pickle
from datetime import datetime

# nltk.download('wordnet')
# nltk.download('punkt')
# nltk.download('stopwords')


def preprocess(tweets: Set[ContentMarketTweet]) -> Tuple[List[List[str]], List[str]]:
    """Preprocess the tweets for NMF topic modelling."""
    corpus = []
    gensim_texts = []
    for tweet in tweets:
        tokens = word_tokenize(tweet.content)

        # pos tag words
        tags = [tag[1] for tag in nltk.pos_tag(tokens)]

        # remove @user and !url
        i = 0
        new_tokens, new_tags = [], []
        while i < len(tokens):
            if i != len(tokens) - 1:
                if tokens[i] == "@" and tokens[i + 1] == "user":
                    i += 2
                elif tokens[i] == "!" and tokens[i + 1] == "url":
                    i += 2
                else:
                    new_tokens.append(tokens[i])
                    new_tags.append(tags[i])
                    i += 1
            else:
                new_tokens.append(tokens[i])
                new_tags.append(tags[i])
                i += 1  
        tokens, tags = new_tokens, new_tags

        # remove numbers
        # remove punctuation and emojis i.e. any word that isn't entirely consisted of alphanumeric 
        # characters
        # remove stopwords
        nums_regex = re.compile('[0-9]+')
        stop_words = stopwords.words('english')
        new_tokens, new_tags = [], []
        for i in range(len(tokens)):
            if not nums_regex.match(tokens[i]) and tokens[i].isalnum() \
                and tokens[i] not in stop_words:
                new_tokens.append(tokens[i])
                new_tags.append(tags[i])
        tokens, tags = new_tokens, new_tags

        # lemmatize words
        new_tokens = []
        for i in range(len(tokens)):
            lemmatized_token = lemmatize(tokens[i], tags[i])
            new_tokens.append(lemmatized_token)
        tokens = new_tokens

        # we can stop caring about the tags after this point
        # remove stopwords again
        stop_words = stopwords.words('english')
        tokens = [token for token in tokens if token not in stop_words]
        corpus.append(" ".join(tokens))
        gensim_texts.append(tokens)

    return gensim_texts, corpus

def lemmatize(text, tag):
    tag_dict = {"JJ": wordnet.ADJ,
                "NN": wordnet.NOUN,
                "VB": wordnet.VERB,
                "RB": wordnet.ADV}

    pos = tag_dict.get(tag[0:2], wordnet.NOUN)
    return WordNetLemmatizer().lemmatize(text, pos=pos)


def find_good_num_topics(texts: List[List[str]]):
    """Find a good number of topics to use for NMF, using gensim.
    
    Source: https://www.kaggle.com/code/rockystats/topic-modelling-using-nmf"""
    # Use Gensim's NMF to get the best num of topics via coherence score
    # Create a dictionary
    # In gensim a dictionary is a mapping between words and their integer id
    dictionary = Dictionary(texts)

    # Filter out extremes to limit the number of features
    # dictionary.filter_extremes(
    #     # no_below=3,  # commented this out
    #     # no_above=0.85,  # commented this out
    #     # keep_n=5000
    # )

    # Create the bag-of-words format (list of (token_id, token_count))
    corpus = [dictionary.doc2bow(text) for text in texts]

    # Create a list of the topic numbers we want to try
    topic_nums = list(np.arange(5, 75 + 1, 5))

    # Run the nmf model and calculate the coherence score
    # for each number of topics
    coherence_scores = []

    for num in topic_nums:
        print(str(num) + "... " + str(datetime.now()))
        nmf = Nmf(
            corpus=corpus,
            num_topics=num,
            id2word=dictionary,
            chunksize=2000,
            passes=5,
            kappa=.1,
            minimum_probability=0.01,
            w_max_iter=300,
            w_stop_condition=0.0001,
            h_max_iter=100,
            h_stop_condition=0.001,
            eval_every=10,
            normalize=True,
            random_state=42
        )
        
        # Run the coherence model to get the score
        cm = CoherenceModel(
            model=nmf,
            texts=texts,
            dictionary=dictionary,
            coherence='c_v'
        )
        
        coherence_scores.append(round(cm.get_coherence(), 5))

    # Get the number of topics with the highest coherence score
    scores = list(zip(topic_nums, coherence_scores))
    best_num_topics = sorted(scores, key=itemgetter(1), reverse=True)[0][0]

    # Plot the results
    fig = plt.figure(figsize=(15, 7))

    plt.plot(
        topic_nums,
        coherence_scores,
        linewidth=3,
        color='#4287f5'
    )

    plt.xlabel("Topic Num", fontsize=14)
    plt.ylabel("Coherence Score", fontsize=14)
    plt.title('Coherence Score by Topic Number - Best Number of Topics: {}'.format(best_num_topics), fontsize=18)
    plt.xticks(np.arange(5, max(topic_nums) + 1, 5), fontsize=12)
    plt.yticks(fontsize=12)

    plt.show()


def plot_top_words(model, feature_names, n_top_words, title):
    """Source: https://scikit-learn.org/stable/auto_examples/applications/plot_topics_extraction_with_nmf_lda.html#sphx-glr-download-auto-examples-applications-plot-topics-extraction-with-nmf-lda-py"""
    fig, axes = plt.subplots(5, 6, figsize=(60, 20), sharex=True)
    axes = axes.flatten()
    for topic_idx, topic in enumerate(model.components_):
        top_features_ind = topic.argsort()[: -n_top_words - 1 : -1]
        top_features = [feature_names[i] for i in top_features_ind]
        weights = topic[top_features_ind]

        ax = axes[topic_idx]
        ax.barh(top_features, weights, height=0.7)
        ax.set_title(f"Topic {topic_idx +1}", fontdict={"fontsize": 10})
        ax.invert_yaxis()
        ax.tick_params(axis="both", which="major", labelsize=7)
        for i in "top right left".split():
            ax.spines[i].set_visible(False)
        fig.suptitle(title, fontsize=20)

    plt.subplots_adjust(top=0.90, bottom=0.05, wspace=0.90, hspace=0.3)
    plt.show()


if __name__ == "__main__":
    config_file_path = "../config.json"
    config_file = open(config_file_path)
    config = json.load(config_file)
    config_file.close()
    # Load from database
    MARKET_LOAD = False
    SPACE_LOAD = False
    DEMAND_SUPPLY_LOAD = False

    # Store to database
    MARKET_STORE = False
    SPACE_STORE = False
    DEMAND_SUPPLY_STORE = False

    # Skip Building
    MARKET_SKIP = False
    SPACE_SKIP = False

    ##########################################################
    # Build DAO Factory and Partitioning
    ##########################################################
    dao_factory = DAOFactory()
    partition = UserPartitioningStrategyFactory.get_user_type_strategy(
        config["partitioning_strategy"])

    ##########################################################
    # Build Content Market
    ##########################################################
    if not MARKET_SKIP:
        market_dao = dao_factory.get_content_market_dao(config["database"])
        market_builder = ContentMarketBuilder(
            config["database"]["content_market_db_name"],
            market_dao, partition)
        if MARKET_LOAD:
            market = market_builder.load()
        else:
            market = market_builder.create()
            if MARKET_STORE:
                market_builder.store(market)

    from analysis import relative_frequency_months
    relative_frequency_months(market)
    
    # # Load all the tweets
    # tweets = sorted(list(market.original_tweets \
    #     .union(market.retweets_of_in_comm)), key=lambda tweet: tweet.id)

    # # tweets = [tweet for tweet in tweets 
    # #           if tweet.created_at.year == 2022 and tweet.created_at.month >= 7 and tweet.created_at.month <= 12]
    # print("Length of tweets: " + str(len(tweets)))

    # # Preprocess
    # print("Creating corpus..." + str(datetime.now()))
    # texts, corpus = preprocess(tweets)
    # print("Done creating corpus... " + str(datetime.now()))

    # # # Store the 
    # # # pickle.dump(texts, open("chess_content_market_tests.pkl", "wb"))
    # # # pickle.dump(corpus, open("chess_content_market_corpus.pkl", "wb"))

    # # # Find the best number of topics to use
    # # find_good_num_topics(texts)

    # # # Actual Model
    # # tf-idf vectorizer with english stopwords
    # print("Tf-idf...")
    # vectorizer = TfidfVectorizer(
    #     # stop_words="english", 
    #     # min_df=3, 
    #     # max_df=0.85, 
    #     # max_features=5000, 
    #     # ngram_range=(1, 2)
    #     )
    # X = vectorizer.fit_transform(corpus)
    
    # n_components = 20

    # print("NMF...")
    # nmf = NMF(
    #     n_components=n_components,
    #     init="nndsvd",  # this works best for sparse data, like what we have
    #     random_state=42,
    #     beta_loss="frobenius",
    #     max_iter=500
    # ).fit(X)

    # # # Getting a df with each topic by document
    # docweights = nmf.transform(vectorizer.transform(corpus))
    # topics = list(docweights.argmax(axis=1))

    # tweet_id_to_topic = {}
    # for i in range(len(tweets)):
    #     tweet_id_to_topic[tweets[i].id] = topics[i]
    # pickle.dump(tweet_id_to_topic, open("ml_content_market_1_all_tweets_" + str(n_components) + "_topics.pkl", "wb"))
    # # tweet_id_to_topic = pickle.load(open("ml_content_market_1_all_tweets_15_topics.pkl", "rb"))
    # # content_type_to_month = {topic: {} for topic in range(n_components)}
    # # month_to_count_total = {}
    # # for tweet_id in tweet_id_to_topic:
    # #     month = datetime(market.get_tweet(tweet_id).created_at.year, market.get_tweet(tweet_id).created_at.month, 1)
    # #     # for month_to_count_total
    # #     if month in month_to_count_total:
    # #         month_to_count_total[month] += 1
    # #     else:
    # #         month_to_count_total[month] = 1

    # #     # for month_to_count_content_type
    # #     if month in content_type_to_month[tweet_id_to_topic[tweet_id]]:
    # #         content_type_to_month[tweet_id_to_topic[tweet_id]][month] += 1
    # #     else:
    # #         content_type_to_month[tweet_id_to_topic[tweet_id]][month] = 1
    
    # # for topic in range(n_components):
    # #     month_to_count_frac = {}
    # #     for month in month_to_count_total:
    # #         if month_to_count_total[month] == 0:
    # #             continue
    # #         else:
    # #             if month not in content_type_to_month[topic]:
    # #                 month_to_count_frac[month] = 0
    # #             else:
    # #                 month_to_count_frac[month] = content_type_to_month[topic][month] / month_to_count_total[month]

    # #     plt.figure(figsize=(10, 7))
    # #     plt.plot(sorted(month_to_count_frac), [month_to_count_frac[month] for month in sorted(month_to_count_frac)])
    # #     plt.title(topic)
    # #     plt.savefig("../results/nmf over time/chess_content_market_filtered_nmf_" + str(n_components) + "_" + str(topic))
    # #     plt.close()


    # # tfidf_feature_names = vectorizer.get_feature_names_out()
    # # plot_top_words(
    # #     nmf, tfidf_feature_names, n_top_words=10, title="Topics in NMF model (Frobenius norm)"
    # # )

    # ### Word frequency #############################################################################
    # # words_list = [["icml"], ["chatgpt"], ["llm", "large language model"]]
    # # for words in words_list:
    # #     month_to_count_content_type = {}
    # #     month_to_count_total = {}
    # #     assert len(tweets) == len(corpus)
    # #     for i in range(len(tweets)):
    # #         tweet_id = tweets[i].id
    # #         month = datetime(market.get_tweet(tweet_id).created_at.year, market.get_tweet(tweet_id).created_at.month, 1)
            
    # #         # for month_to_count_total
    # #         if month in month_to_count_total:
    # #             month_to_count_total[month] += 1
    # #         else:
    # #             month_to_count_total[month] = 1

    # #         # for month_to_count_content_type
    # #         if any(word in corpus[i] for word in words):
    # #             if month in month_to_count_content_type:
    # #                 month_to_count_content_type[month] += 1
    # #             else:
    # #                 month_to_count_content_type[month] = 1
    # #         else:
    # #             if month in month_to_count_content_type:
    # #                 continue
    # #             else:
    # #                 month_to_count_content_type[month] = 0
        
    # #     month_to_count_frac = {}
    # #     for month in month_to_count_total:
    # #         if month_to_count_total[month] == 0:
    # #             continue
    # #         else:
    # #             month_to_count_frac[month] = month_to_count_content_type[month] / month_to_count_total[month]

    # #     plt.figure(figsize=(10, 7))
    # #     plt.plot(sorted(month_to_count_frac), [month_to_count_frac[month] for month in sorted(month_to_count_frac)])
    # #     # plt.ylabel("All Tweets Count")
    # #     plt.title(", ".join(words))
    # #     plt.show()