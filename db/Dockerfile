FROM postgis/postgis:15-3.3

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        osm2pgsql \
        curl && \
    rm -rf /var/lib/apt/lists/*

# Ensure postgres user owns the /osm_data directory
RUN mkdir -p /osm_data && chown -R postgres:postgres /osm_data
