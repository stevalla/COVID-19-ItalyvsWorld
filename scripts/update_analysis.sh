#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the date of yesterday
var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
yesterday=`date -d "1 day ago" +"%Y-%m-%d"`

# set pythonpath env variable
export PYTHONPATH="$folder"/covid_by_ste

######################### LOGISTIC CURVES ############################

# store old logistic curve
mv "$folder"/../results/logistic_curves.png \
    "$folder"/../results/logistic_curves/"$yesterday".png

# recompute cumulative distributions and store the new image
echo "Run python analysis"
python3 -c "$folder"/covid_by_ste/run_analysis.py
