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
python3 -c "import scripts.python.preprocessing as pr; pr.aggregate_data()"
