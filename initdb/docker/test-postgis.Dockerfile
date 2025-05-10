FROM postgis/postgis:15-3.3

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        osm2pgsql \
        curl \
        gosu && \
        ln -s /usr/bin/python3 /usr/bin/python && \
        rm -rf /var/lib/apt/lists/*

# Fix permissions
RUN mkdir -p /osm_data && chown -R postgres:postgres /osm_data
