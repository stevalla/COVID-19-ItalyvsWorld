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
python3 -c "from python.preprocessing import aggregate_data; aggregate_data()"

var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
yesterday=`date -d "1 day ago" +"%Y-%m-%d"`

# Commit new results
git pull
git add "$folder"/../data/*
git commit -m "Added new date ${yesterday}"
git push origin master
