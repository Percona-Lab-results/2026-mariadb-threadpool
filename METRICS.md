# Metrics & Reporting

## Primary Metrics

| Metric | Definition |
|--------|------------|
| **TPS** | Transactions per second (complete BEGIN/COMMIT cycles) |

## Derived Metrics

Performance analysis includes:
- **TPS gain relative to additional RAM**: Throughput improvement when increasing `innodb_buffer_pool_size` from one tier to another
- **TPS gain relative to thread count increase**: Scalability characteristics as concurrent client connections grow

## Output Files

**Per-run telemetry files:**
- `.sysbench.txt` — Sysbench benchmark results
- `.iostat.txt` — I/O statistics
- `.vmstat.txt` — Virtual memory and system statistics
- `.mpstat.txt` — Multi-processor utilization
- `.dstat.txt` — Combined system resource monitoring

**Per-server configuration files:**
- `.cnf.txt` — MariaDB configuration file
- `.vars.txt` — Server variables (`SHOW VARIABLES`)
- `.status.txt` — Server status (`SHOW STATUS`)
- `pt-mysql-summary.txt` — Percona Toolkit system summary
