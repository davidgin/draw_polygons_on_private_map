#!/bin/bash
set -e

echo "🔍 Checking if OSM data exists..."
if psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c '\dt' | grep -q planet_osm_polygon; then
  echo "✅ OSM data already exists, skipping import."
else
  echo "🌍 Importing OSM data..."
  osm2pgsql --create --slim --hstore -d "$POSTGRES_DB" -U "$POSTGRES_USER" /osm_data/planet-latest.osm.pbf
  echo "✅ Import completed."
fi
