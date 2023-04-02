#!/bin/bash

echo "Preprocessing Data..."

# specify data file name here
datafile="../../data/OriginalTweets.json"
temp_location="../../experiments/clean"

python preprocess.py $datafile $temp_location
