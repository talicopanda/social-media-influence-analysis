import numpy as np
import lasagne
import theano
import theano.tensor as T
import sys
import batch_char as batch
import cPickle as pkl
import io
import json
import pymongo
import sys

from t2v import tweet2vec, init_params, load_params
from settings_char import N_BATCH, MAX_LENGTH, MAX_CLASSES


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

    db_config = args[0]
    model_path = args[1]

    with io.open(db_config, 'r') as config_file:
        config = json.load(config_file)

        content_market_db_name = config["database"]["content_market_db_name"]

        client = pymongo.MongoClient()

        db_content_market = client[content_market_db_name]

        collections = [config["database"]["clean_replies_collection"],
            config["database"]["clean_original_tweets_collection"],
            config["database"]["clean_quotes_of_in_community_collection"], 
            config["database"]["clean_quotes_of_out_community_collection"], 
            config["database"]["clean_retweets_of_in_community_collection"], 
            config["database"]["clean_retweets_of_out_community_collection"]]
        
        for collec in collections:
            print("Preparing " + collec + " data...")
            # Test data
            ids = []
            Xt = []
            for tweet in db_content_market[collec].find():
                ids.append(tweet["id"])
                Xc = tweet["text"]
                Xt.append(Xc[:MAX_LENGTH])

            # Model
            print("Loading model params...")
            params = load_params('%s/best_model.npz' % model_path)

            print("Loading dictionaries...")
            with open('%s/dict.pkl' % model_path, 'rb') as f:
                chardict = pkl.load(f)
            with open('%s/label_dict.pkl' % model_path, 'rb') as f:
                labeldict = pkl.load(f)
            n_char = len(chardict.keys()) + 1
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
            print("Processing " + str(numbatches) + " batches...")
            sys.stdout.write("Batch: ")
            for i in range(numbatches):
                sys.stdout.write(str(i + 1) + " ")
                sys.stdout.flush()
                xr = Xt[N_BATCH*i:N_BATCH*(i+1)]
                x, x_m = batch.prepare_data(xr, chardict, n_chars=n_char)
                p = predict(x, x_m)
                e = encode(x, x_m)
                ranks = np.argsort(p)[:, ::-1]
                for idx, item in enumerate(xr):
                    out_pred.append(' '.join(
                        [inverse_labeldict[r] if r in inverse_labeldict else 'UNK' for r in ranks[idx, :5]]))
                    out_emb.append(e[idx, :])

            print()

            # Save
            print("Saving...")
            # with io.open('%s/predicted_tags.txt' % save_path, 'w') as f:
            #     for item in out_pred:
            #         f.write(item + '\n')
            # with open('%s/embeddings.npy'%save_path,'w') as f:
            #    np.save(f,np.asarray(out_emb))

            assert(len(out_emb) == len(out_pred) == len(Xt) == len(ids))

            tweet_embeddings_collection = config["database"]["tweet_embeddings"]
            for i in range(len(ids)):
                db_content_market[tweet_embeddings_collection].insert_one({"id": ids[i], "embedding": list(out_emb[i]), "hashtags": out_pred[i].split(" ")})


if __name__ == '__main__':
    main(sys.argv[1:])
