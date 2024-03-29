import numpy as np
import lasagne
import theano
import theano.tensor as T
import sys
import batch_word as batch
try:
    import cPickle as pkl
except:
    import pickle as pkl
import io
import json

from w2v import tweet2vec, load_params
from settings_word import N_BATCH, N_WORD, MAX_CLASSES


def invert(d):
    out = {}
    for k, v in d.iteritems():
        out[v] = k
    return out


def classify(tweet, t_mask, params, n_classes, n_chars):
    # tweet embedding
    emb_layer = tweet2vec(tweet, t_mask, params, n_chars)
    # Dense layer for classes
    l_dense = lasagne.layers.DenseLayer(
        emb_layer, n_classes, W=params['W_cl'], b=params['b_cl'], nonlinearity=lasagne.nonlinearities.softmax)

    return lasagne.layers.get_output(l_dense), lasagne.layers.get_output(emb_layer)


def main(args):

    data_path = args[0]
    model_path = args[1]
    save_path = args[2]
    if len(args) > 3:
        m_num = int(args[3])

    print("Preparing Data...")
    # Test data
    Xt = []
    with io.open(data_path + "_text.txt", 'r', encoding='utf-8') as f:
        for line in f:
            Xc = line.rstrip('\n')
            Xt.append(Xc)

    # Model
    print("Loading model params...")
    if len(args) > 3:
        params = load_params('%s/model_%d.npz' % (model_path, m_num))
    else:
        params = load_params('%s/best_model.npz' % model_path)

    print("Loading dictionaries...")
    with open('%s/dict.pkl' % model_path, 'rb') as f:
        chardict = pkl.load(f)
    with open('%s/label_dict.pkl' % model_path, 'rb') as f:
        labeldict = pkl.load(f)
    n_char = min(len(chardict.keys()) + 1, N_WORD)
    n_classes = min(len(labeldict.keys()) + 1, MAX_CLASSES)
    inverse_labeldict = invert(labeldict)

    print("Building network...")
    # Tweet variables
    tweet = T.itensor3()
    t_mask = T.fmatrix()

    # network for prediction
    predictions, embeddings = classify(
        tweet, t_mask, params, n_classes, n_char)
    # Theano function
    print("Compiling theano functions...")
    predict = theano.function([tweet, t_mask], predictions)
    encode = theano.function([tweet, t_mask], embeddings)

    # Test
    print("Encoding...")
    out_pred = []
    out_emb = []
    numbatches = len(Xt)/N_BATCH + 1
    for i in range(numbatches):
        xr = Xt[N_BATCH*i:N_BATCH*(i+1)]
        x, x_m = batch.prepare_data(xr, chardict, n_tokens=n_char)
        p = predict(x, x_m)
        e = encode(x, x_m)
        ranks = np.argsort(p)[:, ::-1]

        for idx, item in enumerate(xr):
            out_pred.append(' '.join([inverse_labeldict[r]
                                      for r in ranks[idx, :5]]))
            out_emb.append(e[idx, :])

    # Save
    print("Saving...")
    # with io.open('%s/predicted_tags.txt' % save_path, 'w') as f:
    #    for item in out_pred:
    #        f.write(item + '\n')
    # with open('%s/embeddings.npy' % save_path, 'w') as f:
    #    np.save(f, np.asarray(out_emb))

    assert(len(out_emb) == len(out_pred) == len(Xt))

    id_to_embeddings = {}
    id_to_hashtags = {}
    id_to_text = {}
    with io.open(data_path + "_ids.txt", 'r', encoding='utf-8') as f:
        i = 0
        for line in f:
            id = int(line.rstrip())
            id_to_embeddings[id] = out_emb[i].tolist()
            id_to_hashtags[id] = out_pred[i].split(" ")
            id_to_text[id] = Xt[i]
            i += 1

    with open('%s/medium_embeddings.json' % save_path, 'w') as f:
        json.dump(id_to_embeddings, f)
    with open('%s/medium_hashtags.json' % save_path, 'w') as f:
        json.dump(id_to_hashtags, f)
    with open('%s/medium_text.json' % save_path, 'w') as f:
        json.dump(id_to_text, f)


if __name__ == '__main__':
    main(sys.argv[1:])
