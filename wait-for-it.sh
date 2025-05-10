#!/usr/bin/env bash
# wait-for-it.sh

# Modified from https://github.com/vishnubob/wait-for-it

# Description:
# This script waits for a service at a given host and port to become available.
# It will exit 0 when the service is available, otherwise, it will exit 1.

TIMEOUT=15
STRICT=false
WAIT_HOSTS=()

# Parse arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --timeout)
            TIMEOUT="$2"
            shift 2
            ;;
        --strict)
            STRICT=true
            shift
            ;;
        *)
            WAIT_HOSTS+=("$1")
            shift
            ;;
    esac
done

# Function to check if the service is up
check_service() {
    nc -z "$1" "$2"
}

# Wait for each host:port pair
for host in "${WAIT_HOSTS[@]}"; do
    IFS=":" read -r -a hostport <<< "$host"
    host="${hostport[0]}"
    port="${hostport[1]}"

    echo "Waiting for $host:$port to be available..."

    for i in $(seq 1 "$TIMEOUT"); do
        if check_service "$host" "$port"; then
            echo "$host:$port is available!"
            break
        else
            echo "$host:$port is not available yet..."
            sleep 1
        fi
    done

    if ! check_service "$host" "$port"; then
        echo "Timeout while waiting for $host:$port"
        if $STRICT; then
            exit 1
        fi
    fi
done

