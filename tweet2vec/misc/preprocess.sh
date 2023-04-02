#!/bin/bash

echo "Preprocessing Data..."

# specify data file name here
config_file="../../config.json"

python preprocess.py $config_file
