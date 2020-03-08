#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# world
echo "Scanning world"
bash "$folder"/download_data.sh world

# italian
echo "Scanning Italy"
bash "$folder"/download_data.sh italy

# aggregate italian and world
echo "Aggregating"
# python3 "$folder"/python/aggregate_data.py

var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
today=`date +"%Y-%m-%d"`

# Commit new results
git pull
git add "$folder"/../data/*
git commit -m "Added new date ${today}"
git push origin master
