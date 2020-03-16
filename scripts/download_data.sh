#!/usr/bin/env bash

country=$1

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
link=$(cat "$folder"/links | grep "$country" | sed "s/$country=\(.*\)/\1/g")
country_folder="$folder"/../data/"$country"

# Read the date of today
var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
yesterday=`date -d "1 day ago" +"%Y-%m-%d"`
day=$(date -d "$yesterday" '+%d')

# Every 10 days download all the data to upgrade old data
if [[ $(( 10#$day % 10 )) -eq 0 ]]; then
    rm "$folder"/../data/*.csv
fi

rm -f "$country_folder"/*.csvk

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
cp "$working_folder"/*.csv "$country_folder"

# Update data
python3 "$folder"/python/preprocessing.py "$country"

# Store history
for file in "$country_folder"/*.csv; do
    filename=$(basename -- "$file")
    f="${filename%.*}"
    mv "$file" "$country_folder"/history/"$f"_"$yesterday".csv
done

# Cleaning
rm -r "$working_folder"
rm -f "$country_folder"/*.csv
