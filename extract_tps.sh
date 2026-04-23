#!/bin/bash

# Extract TPS from sysbench files
extract_tps() {
    local file=$1
    grep "transactions:" "$file" | grep -oP '\(\K[0-9.]+(?= per sec)'
}

echo "Server,Version,Tier,Threads,TPS"

# MariaDB (non-thread-pool)
for version in 11.8.6-MariaDB-ubu2404 12.2.2-MariaDB-ubu2404; do
    for file in benchmark_logs/mariadb/$version/*.sysbench.txt; do
        [ -f "$file" ] || continue
        tier=$(basename "$file" | grep -oP 'Tier\K[0-9]+')
        threads=$(basename "$file" | grep -oP '_\K[0-9]+(?=th)')
        tps=$(extract_tps "$file")
        echo "MariaDB,$version,${tier}G,$threads,$tps"
    done
done

# MySQL
for version in 8.4.8 9.7.0-er2; do
    for file in benchmark_logs/mysql/$version/*.sysbench.txt; do
        [ -f "$file" ] || continue
        tier=$(basename "$file" | grep -oP 'Tier\K[0-9]+')
        threads=$(basename "$file" | grep -oP '_\K[0-9]+(?=th)')
        tps=$(extract_tps "$file")
        echo "MySQL,$version,${tier}G,$threads,$tps"
    done
done

# Percona
for version in 8.4.8-8; do
    for file in benchmark_logs/percona/$version/*.sysbench.txt; do
        [ -f "$file" ] || continue
        tier=$(basename "$file" | grep -oP 'Tier\K[0-9]+')
        threads=$(basename "$file" | grep -oP '_\K[0-9]+(?=th)')
        tps=$(extract_tps "$file")
        echo "Percona,$version,${tier}G,$threads,$tps"
    done
done
