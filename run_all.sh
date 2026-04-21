#!/bin/bash

# Check if Docker is installed
if ! command -v docker >/dev/null 2>&1; then
    echo "Error: Docker is not installed." >&2
    exit 1
fi

# Check if MySQL client is installed
if ! command -v mysql >/dev/null 2>&1; then
    echo "Error: MySQL client is not installed." >&2
    exit 1
fi

# Check if current user is in the docker group
if ! groups "$USER" | grep -q "\bdocker\b"; then
    echo "Error: User '$USER' is not in the docker group." >&2
    exit 1
fi


sudo apt update
sudo apt install sysstat sysbench dstat -y


./run_pt_summary.sh
./run_pt_mysql_summary.sh

IS_READ_ONLY="0"
ENABLE_THREAD_POOL="1"

VERSIONS=("11.8.6" "12.2.2")

for VERSION in "${VERSIONS[@]}"; do
  ./run_metrics.sh "mariadb" "$VERSION" "$IS_READ_ONLY" "$ENABLE_THREAD_POOL"
done

echo "All benchmarks completed!"