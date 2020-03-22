#!/usr/bin/env bash

country=$1

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
link=$(cat "$folder"/links | grep "$country" | sed "s/$country=\(.*\)/\1/g")
data_folder="$folder"/../data

# Read the date of yesterday
var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
yesterday=`date -d "1 day ago" +"%Y-%m-%d"`
day=$(date -d "$yesterday" '+%d')

# Every 10 days download all the data to upgrade old data
if [[ $(( 10#$day % 10 )) -eq 0 ]]; then
    echo "Reloading all the data"
    rm "$folder"/../data/cleaned/*.csv
fi

# Download new world data
if [[ "$country" == "italy" ]]; then
    mkdir "$folder"/italy_data
    working_folder="$folder"/italy_data
    wget -q -P "$working_folder" "$link"
else
    mkdir "$folder"/world_data
    working_folder="$folder"/world_data
    svn checkout "$link" "$working_folder"
    working_folder="$working_folder"
fi

# Copy to working folder
cp "$working_folder"/*.csv "$data_folder"

# Update data
python3 "$folder"/covid_by_ste/preprocessing/preprocessing.py "$country"

# Store history
for file in "$data_folder"/*.csv; do
    filename=$(basename -- "$file")
    f="${filename%.*}"
    mv "$file" "$data_folder"/history/"$country"/"$f"_"$yesterday".csv
done

# Cleaning
rm -r "$working_folder"
rm -f "$data_folder"/*.csv
