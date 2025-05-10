#!/bin/bash
set -e

echo "🚀 Running OSM import via Python..."
python3 /docker-entrypoint-initdb.d/osm_import.py