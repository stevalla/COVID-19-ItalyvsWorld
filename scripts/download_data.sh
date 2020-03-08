#!/usr/bin/env bash

country=$1

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
link=$(cat "$folder"/links | grep "$country" | sed "s/$country=\(.*\)/\1/g")
data_folder="$folder"/../data/"$country"

# Read the date of today
var=`date +"%FORMAT_STRING"`
now=`date +"%m_%d_%Y"`
today=`date +"%Y-%m-%d"`

rm -f "$data_folder"/*.csv

# Download new world data
if [[ "$country" == "italy" ]]; then
    mkdir "$folder"/italy_data
    working_folder="$folder"/italy_data
    wget -q -P "$working_folder" "$link"
else
    working_folder="$folder"/csse_covid_19_time_series
    svn checkout "$link"
fi

# Copy to working folder
cp "$working_folder"/*.csv "$data_folder"

# Update data
python3 "$folder"/python/preprocessing.py "$country"

# Clean
mv "$data_folder"/*.csv "$data_folder"/history
rm -r "$working_folder"
rm -f "$data_folder"/*.csv

