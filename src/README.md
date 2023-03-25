# Setup and Requirements

Ensure you have a version of Python3 installed by confirming that `python -V` outputs `Python 3.*.*`.

Open a terminal window and ensure that you are in the top directory of `/src` folder. Then:

1. Run `python -m venv env`
2. Run `venv/Scripts/activate` (Windows) or `source venv/bin/activate` (MacOS)
3. Install all dependencies with `pip install -r requirements.txt`

To deactivate the virtual environment, run `deactivate`.

# Generating Embedded Data

In this project we use latent embedding of strings to semantically represent each tweet as explained in more details on the project's `README.md` file. As such, we provide three out-of-the-box methods of content embedding:

1. Tweet2Vec
2. Medium Dataset Baseline

We also provide a copy of the `tweet2vec` library that allows you to train an embedding model from scratch for the given data, if necessary.

Please refer to `/tweet2vec/INTRUCTIONS.md` file for details on how to run the two embeddings provided aobve them.
