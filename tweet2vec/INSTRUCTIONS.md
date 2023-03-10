# Setup and Requirements

Depending on your operating system, follow the instructions below to run the program.

## MacOS/Linux

### Requirements

Download and install [Python 2.7](https://www.python.org/downloads/release/python-2718/) if you don't already have it. Confirm that `python -V` outputs `Python 2.7.*`.

### Setup

Open a terminal window and ensure that you are in the top directory of the outermost `/tweet2vec` folder. Then:

1. Run `pip2 install virtualenv`
2. Run `which python2` and denote the output to be `<python_path>`
3. Run `virtualenv <python_path> venv` using `<python_path>` from above 
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

# Embedding Data

## Tweet2Vec Algorithm

Create a directory to store your results (e.g. `mkdir ../embedding_tweet2vec`). Now you can encode your data by running:

`python ./tweet2vec/encode_char.py ./<path_to_file>/tweets.txt ./tweet2vec/best_model/ ../embedding_tweet2vec`

## Medium Data Baseline

Create a directory to store your results (e.g. `mkdir ../embedding_medium`). Now you can encode your data by running:

`python ./baseline/encode_word.py ./<path_to_file>/tweets.txt ./baseline/best_model/ ../embedding_medium`
