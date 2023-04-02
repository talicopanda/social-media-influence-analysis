#!/bin/bash

echo "Preprocessing Data..."

# specify data file name here
datafile="../../data/OriginalTweets.json"
temp_location="../../experiments/clean"

python preprocess.py $datafile $temp_location

# specify result path here
resultpath="../../results"

mkdir -p $resultpath

echo "Encoding Data..."

# ===== Tweet2Vec =====

modelpath="../tweet2vec/best_model/"
python ../tweet2vec/encode_char.py $temp_location $modelpath $resultpath

# ===== Baseline =====

modelpath="../baseline/best_model/"
python ../baseline/encode_word.py $temp_location $modelpath $resultpath
