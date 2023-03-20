#!/bin/bash

echo "Preprocssing Data..."

# specify data file name here
datafile="./shortTweets.json"
temp_name="clean_tweet"

python preprocess.py $datafile $temp_name

# specify result path here
resultpath="./results"

mkdir -p $resultpath

echo "Running Model..."

python ../word2vec.py $temp_name $resultpath