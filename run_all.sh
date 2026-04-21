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
VERSIONS=("11.8.6" "12.2.2")
THREAD_POOL_OPTIONS=("0" "1")  # 0=disabled, 1=enabled

for ENABLE_THREAD_POOL in "${THREAD_POOL_OPTIONS[@]}"; do
  echo ""
  echo "=========================================================================="
  if [ "$ENABLE_THREAD_POOL" -eq 1 ]; then
    echo "=== Running benchmarks WITH Thread Pool enabled ==="
  else
    echo "=== Running benchmarks WITHOUT Thread Pool (default one-thread-per-connection) ==="
  fi
  echo "=========================================================================="
  echo ""

  for VERSION in "${VERSIONS[@]}"; do
    ./run_metrics.sh "mariadb" "$VERSION" "$IS_READ_ONLY" "$ENABLE_THREAD_POOL"
  done
done

echo ""
echo "=========================================================================="
echo "All benchmarks completed!"
echo "=========================================================================="