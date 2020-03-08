#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
working_folder="$folder"/csse_covid_19_time_series
data_folder="$folder"/../data/world

rm -f "$data_folder"/*.csv

# Download new world data
svn checkout https://github.com/CSSEGISandData/COVID-19/trunk/csse_covid_19_data/csse_covid_19_time_series

date=

# Copy to working folder
cp "$working_folder"/*.csv "$data_folder"

# Update data
python3 "$folder"/python/world_preprocessing.py


# Clean
mv "$data_folder"/*.csv "$data_folder"/history
rm -r "$working_folder"
rm -f "$data_folder"/*.csv

# Commit new results
git add "$folder"/../data/*
git commit -m "Added new date $date"
git push origin master

