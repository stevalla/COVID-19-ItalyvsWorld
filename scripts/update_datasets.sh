#!/usr/bin/env bash

folder="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# world
echo "Scanning world"
bash "$folder"/download_data.sh world

# italian
echo "Scanning Italy"
bash "$folder"/download_data.sh italy

# aggregate italian and world
cd "$folder"
echo "Aggregating"
python3 -c "import covid_by_ste.preprocessing as pr; pr.aggregate_data()"
