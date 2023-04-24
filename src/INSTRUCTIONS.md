# Setup and Requirements

Ensure you have a version of Python3 installed by confirming that `python -V` outputs `Python 3.*.*`.

Open a terminal window and ensure that you are in the top directory of `/src` folder. Then:

1. Run `python -m venv env`
2. Run `venv/Scripts/activate` (Windows) or `source venv/bin/activate` (MacOS)
3. Install all dependencies with `pip install -r requirements.txt`

To deactivate the virtual environment, run `deactivate`.

# Generating Embedded Data

In this project we use latent embedding of strings to semantically represent each tweet as explained in more details on the project's main `README.md` file in the top directory. As such, we provide two out-of-the-box methods of content embedding:

1. Tweet2Vec
2. Medium Dataset Baseline

To generate these out-of-the-box embeddings, please refer to `/tweet2vec/INTRUCTIONS.md` file for details.

We also provide a copy of the `tweet2vec` library that allows you to train an embedding model from scratch for any given data.

