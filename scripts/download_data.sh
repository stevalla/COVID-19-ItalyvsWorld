#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
data_folder="$folder"/csse_covid_19_time_series
working_folder="$folder"/../data/world

rm "$working_folder"/*

# Download new world data
svn checkout https://github.com/CSSEGISandData/COVID-19/trunk/csse_covid_19_data/csse_covid_19_time_series

# Copy to working folder
cp "$data_folder"/*.csv "$folder"/../publication/world/

# Update data
python3 "$folder"/world_preprocessing.py

# Clean
rm -r "$data_folder"
