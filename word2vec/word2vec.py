import numpy as np
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import sys
import io
from gensim import models
import json

# same as tweet2vec for consistency
MAX_LENGTH = 285

# import the word2vec model to memory (check README for download link)
word2vec_model = models.KeyedVectors.load_word2vec_format('GoogleNews-vectors-negative300.bin.gz',
                                                          binary=True)

punctuation_traslator = str.maketrans('', '', string.punctuation)
stop_words = set(stopwords.words('english'))


def text2vec(text):
    """
    Returns a vector representation of text from the mean of the individual word embedding vectors.
    """
    text = text.lower()
    text = text.translate(punctuation_traslator)
    text = word_tokenize(text)
    filtered_sentence = [w for w in text if not w in stop_words]
    i = 1
    vector_representation = np.zeros((1, 300))

    for word in filtered_sentence:
        try:
            vector_representation = vector_representation + \
                word2vec_model[word]
            i = i + 1
        except KeyError:
            i = i
    vector_representation = np.divide(vector_representation, i)
    return vector_representation


if __name__ == '__main__':
    data_path = sys.argv[1]
    save_path = sys.argv[2]

    Xt = []
    with io.open(data_path + "_text.txt", 'r', encoding='utf-8') as f:
        for line in f:
            Xc = line.rstrip('\n')
            Xt.append(Xc[:MAX_LENGTH])

    out_emb = []
    for t in Xt:
        out_emb.append(text2vec(t))

    id_to_tweets = {}
    with io.open(data_path + "_ids.txt", 'r', encoding='utf-8') as f:
        i = 0
        for line in f:
            id_to_tweets[int(line.rstrip())] = out_emb[i]
            i += 1
    with open('%s/word2vec_embeddings.json' % save_path, 'w') as f:
        json.dump(id_to_tweets, f)
