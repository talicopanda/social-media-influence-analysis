# Setup and Requirements

Ensure you have a version of Python3 installed by confirming that `python -V` outputs `Python 3.*.*`.

Open a terminal window and ensure that you are in the top directory of `/src` folder. Then:

1. Run `python -m venv env`
2. Run `venv/Scripts/activate` (Windows) or `source venv/bin/activate` (MacOS)
3. Install all dependencies with `pip install -r requirements.txt`

To deactivate the virtual environment, run `deactivate`.

# Preprocessing Data

The Twitter API returns a json file with unnecessary extra fields that might affect performance for larger files. In addition, a tweet may have unwanted hashtags, HTML tags, usernames and URLs. Therefore, we levarega some of `tweet2vec`'s data preprocessor with a few changes to perform some data cleaning.

`python /tweet2vec/misc/preprocessor.py <path_to_data>/tweets.json clean_tweet`

And this will generate two text files `clean_tweet_ids.txt` and `clean_tweet_text.txt` that are the clean and ordered text from the tweets and their corresponding ids.

`clean_tweet_text.txt` can be loaded directly into the models to obtain latent embeddings.

For ease of user, we create a script `./preprocess_and_encode.sh` that takes in a raw json file of tweets from the Twitter API, preprocess the data according to our standards and embedds the data according to our models.

# Generating Embedded Data

For Word2Vec Average, make sure you use this folder's virtual environment as outlined above. Now, download the model from this [drive](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?resourcekey=0-wjGZdNAUop6WykTtMip30g) and place it under the `word2vec` folder (the same directory as `word2vec.py` is in).

Ensure your tweet data json file (the tweet data from Twitter's API) is the `misc` folder, and ensure you are in `misc` by running `cd misc`. Then, run the following command to generate your embeddings:

`./preprocess_and_encode.sh`

Note: you might have to donwload "punkt" by spawning a python interpreter (run `python` on the terminal) and running the following two commands:

1. `import nltk`
2. `nltk.download("punkt")`

At this point you may quit the interpreter by running `exit()`.
