# Setup and Requirements

Depending on your operating system, follow the instructions below to run the program.

## MacOS/Linux

### Requirements

Download and install [Python 2.7](https://www.python.org/downloads/release/python-2718/) if you don't already have it. Confirm that `python -V` outputs `Python 2.7.*`.

### Setup

Open a terminal window and ensure that you are in the top directory of the outermost `/tweet2vec` folder. Then:

1. Run `pip2 install virtualenv`
2. Run `which python2` and denote the output to be `<python_path>`
3. Run `virtualenv -p <python_path> venv` using `<python_path>` from above
4. Run `source venv/bin/activate`
5. Install all dependencies with `pip install -r requirements.txt`

To deactivate the virtual environment, run `deactivate`.

## Windows

### Requirements

Download and install [Python 2.7](https://www.python.org/downloads/release/python-2718/) if you don't already have it. Check the path to the directory where python 2.7 is installed in your system (usually of the form `<path>\Python27\`).

Also donwnload and install [MinGW C++](https://github.com/niXman/mingw-builds-binaries/releases) from one of the 64-bit release versions outlined in that github. Here is a [video](https://www.youtube.com/watch?v=dRxPUblx2SY&ab_channel=AnielMaharajh) that may help.

### Setup

Open PowerShell window and ensure that you are in the top directory of the outermost `/tweet2vec` folder. Then:

1. Run `<path>\Python27\Scripts\pip.exe install virtualenv`
2. Run `<path>\Python27\Scripts\virtualenv.exe venv`
3. Run `venv/Scripts/activate`
4. Confirm that `python -V` outputs `Python 2.7.*`
5. Confirm that `pip -V` outputs `pip 20.3.4 from <path_to_pip> (python 2.7)`
6. Install all dependencies with `pip install -r requirements.txt`

To deactivate the virtual environment, run `deactivate`.

# Preprocessing Data

The Twitter API returns a json file with unnecessary extra fields that might affect performance for larger files. In addition, a tweet may have unwanted hashtags, HTML tags, usernames and URLs. Therefore, we levarega some of `tweet2vec`'s data preprocessor with a few changes to perform some data cleaning.

`python /tweet2vec/misc/preprocessor.py <path_to_data>/tweets.json clean_tweet`

And this will generate two text files `clean_tweet_ids.txt` and `clean_tweet_text.txt` that are the clean and ordered text from the tweets and their corresponding ids.

`clean_tweet_text.txt` can be loaded directly into the models to obtain latent embeddings.

For ease of user, we create a script `./preprocess_and_encode.sh` that takes in a raw json file of tweets from the Twitter API, preprocess the data according to our standards and embedds the data according to our models.

# Embedding Data

Ensure your tweet data json file (the tweet data from Twitter's API) is the `misc` folder, and ensure you are in `misc` by running `cd misc`. Then, run the following command to generate your embeddings:

`./preprocess_and_encode.sh`
