#!/bin/bash

echo "Preprocessing Data..."

# specify data file name here
datafile="../../data/UserTweets.json"
temp_location="../../experiments/clean_tweet"

python preprocess.py $datafile $temp_location

# specify result path here
resultpath="../../results"

mkdir -p $resultpath

# ===== Tweet2Vec =====

modelpath="../tweet2vec/best_model/"
python ../tweet2vec/encode_char.py $temp_name $modelpath $resultpath

# ===== Baseline =====

modelpath="../baseline/best_model/"
python ../baseline/encode_word.py $temp_name $modelpath $resultpath
