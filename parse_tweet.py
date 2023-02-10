"""
TODO: Discussion

There are three approaches to try once we have data to test and compare
1) We use Google's word2vec embedding by averaging the words individual embeddings
2) Rely on tweet2vec's baseline encoder
3) Use tweet2vec to train an encoder based on our community's data

(1) is presented below, (2) and (3) rely on code from https://github.com/bdhingra/tweet2vec/
"""

import numpy as np
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string

import gensim

# import the word2vec model to memory
word2vec_model = gensim.models.KeyedVectors.load_word2vec_format(
    '/Volumes/PICS/pyProject/GoogleNews-vectors-negative300.bin.gz',
    binary=True)

punctuation_traslator = str.maketrans('', '', string.punctuation)
stop_words = set(stopwords.words('english'))


def text2vec(text):
    """
    Returns a vector representation of text from the mean of the individual word embedding vectors.
    """
    text = text.lower()
    text = text.translate(punctuation_traslator)
    text = nltk.word_tokenize(text)
    filtered_sentence = [w for w in text if not w in stop_words]
    i = 1
    vector_representation = np.zeros((1, 300))

    for word in filtered_sentence:
        try:
            vector_representation = vector_representation + \
                word2vec_model.wv[word]
            i = i + 1
        except KeyError:
            i = i
    vector_representation = np.divide(vector_representation, i)
    return vector_representation
