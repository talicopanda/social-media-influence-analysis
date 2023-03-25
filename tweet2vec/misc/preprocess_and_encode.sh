#!/bin/bash

echo "Preprocssing Data..."

# specify data file name here
datafile="./shortTweets.json"
temp_name="clean_tweet"

python preprocess.py $datafile $temp_name

# specify result path here
resultpath="./results"

mkdir -p $resultpath

# ===== Tweet2Vec =====

# modelpath="../tweet2vec/best_model/"
# python ../tweet2vec/encode_char.py $temp_name $modelpath $resultpath

# ===== Baseline =====

modelpath="../baseline/best_model/"
python ../baseline/encode_word.py $temp_name $modelpath $resultpath
