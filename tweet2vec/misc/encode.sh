#!/bin/bash

db_config="../../config.json"

mkdir -p $resultpath

echo "Encoding Data..."

# ===== Tweet2Vec =====

modelpath="../tweet2vec/best_model/"
python ../tweet2vec/encode_char_from_db.py $db_config $modelpath

# # ===== Baseline =====

# modelpath="../baseline/best_model/"
# python ../baseline/encode_word_from_db.py $db_config $modelpath
