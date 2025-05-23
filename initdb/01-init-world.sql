--- # Project Setup: FastAPI + PostGIS + OSM (NYC for test, World for prod)

-- The script initializes the database for the FastAPI application with PostGIS and OSM data.
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

CREATE SEQUENCE IF NOT EXISTS client_id_seq;

CREATE TABLE IF NOT EXISTS polygons (
  id SERIAL PRIMARY KEY,
  client_id INTEGER NOT NULL DEFAULT nextval('client_id_seq'),
  name VARCHAR(255) NOT NULL,
  polygon GEOMETRY(POLYGON, 4326) NOT NULL
);