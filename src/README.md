# Setup and Requirements

Ensure you have a version of Python3 installed by confirming that `python -V` outputs `Python 3.*.*`.

Open a terminal window and ensure that you are in the top directory of `/tweet2vec` folder. Then:

1. Run `python -m venv`
2. Run `venv/Scripts/activate`
3. Install all dependencies with `pip install -r requirements.txt`

To deactivate the virtual environment, run `deactivate`.

# Generating Embedded Data

In this project we use latent embedding of strings to semnatically represent each tweet as explained in more details on the project's `README.md` file. As such, we provide three different methods of content embedding:

1. Tweet2Vec
2. Medium Dataset Baseline
3. Word2Vec Average

For the first two embeddings, refer to `/tweet2vec/INTRUCTIONS.md` file for details on how to run them.

For Word2Vec Average, use this folder's virtual environment as outlined in [Setup and Requirements](#setup-and-requirements), create a directory to store your results (e.g. `mkdir ../embedding_word2vec`). Now, download the model from this [drive](https://drive.google.com/file/d/0B7XkCwpI5KDYNlNUTTlSS21pQmM/edit?resourcekey=0-wjGZdNAUop6WykTtMip30g) and place it under `src` (the same directory as `word2vec.py` is). Now run:

`python word2vec.py ./<path_to_file>/tweets.txt ../embedding_word2vec`

Note: you might have to donwload "punkt" by spawning a python interpreter (run `python` on the terminal) and running the following two commands:

1. `import nltk`
2. `nltk.download("punkt")`

At this point you may quit the interpreter by running `exit()`.
