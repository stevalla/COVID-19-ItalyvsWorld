#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Read the date of yesterday
var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
yesterday=`date -d "1 day ago" +"%Y-%m-%d"`

# set pythonpath env variable
export PYTHONPATH="$folder"/covid_by_ste

declare -a datasets=("world" "italy")

echo "Downloading data"
for country in "${datasets[@]}"; do
    # preprocessing data
    echo "Scanning ${country}"
    bash "$folder"/download_data.sh ${country}
done

echo "Preprocessing data"
python3 -c "import data_preparation.preprocessing as pr; pr.preprocess_data()"

for country in "${datasets[@]}"; do
    # Store history
    for file in "$folder"/../data/"$country"/*.csv; do
        filename=$(basename -- "$file")
        f="${filename%.*}"
        mv "$file" "$folder"/../data/history/"$country"/"$f"_"$yesterday".csv
    done
    # Cleaning
    rm -r "$folder"/${country}_data
    rm -r "$folder"/../data/"$country"
done
