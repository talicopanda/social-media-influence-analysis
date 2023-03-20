#!/bin/bash

# specify data file name here
datafile="./encoder_example.txt"

python preprocessor.py $datafile clean_tweet

# specify result path here
resultpath="./results"

mkdir -p $resultpath

# ===== Tweet2Vec =====

modelpath="../tweet2vec/best_model/"
python ../tweet2vec/encode_char.py $datafile $modelpath $resultpath

# ===== Baseline =====

# modelpath="../baseline/best_model/"
# python ../baseline/encode_word.py $datafile $modelpath $resultpath