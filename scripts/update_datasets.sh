#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the date of yesterday
var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
yesterday=`date -d "1 day ago" +"%Y-%m-%d"`

# set pythonpath env variable
export PYTHONPATH="$folder"/covid_by_ste

# preprocessing world data
echo "Scanning world"
bash "$folder"/download_data.sh world

# preprocessing italian data
echo "Scanning Italy"
bash "$folder"/download_data.sh italy

# aggregate italian and world data
echo "Aggregating"
python3 -c "import covid_by_ste.preprocessing as pr; pr.aggregate_data()"

# TODO: add check of new data
