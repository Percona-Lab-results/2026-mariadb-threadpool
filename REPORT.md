# MariaDB, MySQL and Percona Server OLTP Performance - NVMe Storage and Configuration Optimization

## 1. Interactive Graphs

An interactive web-based visualization of all benchmark results is available online:

**[View Interactive Performance Graphs](https://percona-lab-results.github.io/2026-mariadb-threadpool/sysbench_oltp_rw_comparison_mariadb.html)**

This interactive tool allows you to:
- Compare performance across all tested servers and configurations
- Filter by memory tier (2GB, 12GB, 32GB)
- Select specific thread counts for detailed analysis
- View raw benchmark data and configuration files
- Explore TPS metrics dynamically

## 2. Benchmark Overview

### 2.1. Purpose and Scope

### Purpose

This benchmark study compares MariaDB performance against MySQL and Percona Server on fast storage with optimized configuration. All servers are tested with:

- **NVMe storage** for high-performance testing
- **Optimized I/O configuration** to match NVMe capabilities (`innodb_io_capacity=10000`, 16 I/O threads)
- **Thread pool testing** as a secondary experiment for MariaDB

The goal is to evaluate how MariaDB 11.8.6 and 12.2.2 perform compared to MySQL 8.4.8, MySQL 9.7.0-er2, and Percona Server 8.4.8 on fast storage with optimized settings.

### Target Questions

This analysis seeks to answer the following key questions:

1. **Primary Comparison: MariaDB vs MySQL and Percona Server**
   - How does MariaDB 11.8.6 and 12.2.2 with optimized I/O configuration on NVMe storage compare to MySQL 8.4.8, MySQL 9.7.0-er2, and Percona Server 8.4.8?
   - How do MariaDB versions perform across different memory tiers (I/O bound, mixed, memory-resident workloads)?

2. **Thread Pool as Secondary Experiment**
   - Does thread pool provide additional value on top of NVMe storage?
   - Are the thread pool benefits observed with fast storage consistent with expectations?
   - When would thread pool be recommended given NVMe baseline performance?

### Scope

- **Primary Comparison**: MariaDB 11.8.6 and 12.2.2 vs MySQL 8.4.8, MySQL 9.7.0-er2, and Percona Server 8.4.8 on NVMe storage with optimized I/O configuration
- **Secondary Test**: Thread Pool configuration (with and without) for MariaDB
- **Workload Type**: Sysbench OLTP Read-Write
- **Concurrency Levels**: 1, 4, 16, 32, 64, 128, 256, 512 client threads
- **Memory Tiers**: 2 GB, 12 GB, 32 GB `innodb_buffer_pool_size`
- **Thread Pool Configuration**: `thread_pool_size=80`, `thread_pool_max_threads=2000`

### 2.2. Configurations Under Test

| Server | Version | Thread Handling | Role |
|--------|---------|----------------|------|
| **MariaDB** | 11.8.6 | Default | Primary comparison |
| **MariaDB** | 11.8.6 | Thread Pool | Secondary: thread pool test |
| **MariaDB** | 12.2.2 | Default | Primary comparison |
| **MariaDB** | 12.2.2 | Thread Pool | Secondary: thread pool test |
| **MySQL** | 8.4.8 | Default | Primary comparison |
| **MySQL** | 9.7.0-er2 | Default | Primary comparison |
| **Percona Server** | 8.4.8-8 | Default | Primary comparison |

## 3. Key Findings

This section summarizes the critical performance insights from comparing all database servers, highlighting which versions excel or struggle in different scenarios.

### 3.1. Performance by Workload Type

Performance varies significantly across database engines and versions depending on workload characteristics:

#### 3.1.1. Memory-Resident Workloads (32GB Buffer Pool)

**Winner: MariaDB dominates when the full dataset fits in memory**

![Memory-Resident Table](graphs_out/table_tps_32g.png)

![Memory-Resident Performance](graphs_out/throughput_tps_32g.png)

**Top performers at 128 threads:**
1. **MariaDB 11.8.6: 10,694 TPS** - Best overall
2. MySQL 9.7.0: 9,374 TPS (-12% vs leader)
3. Percona Server 8.4.8: 8,483 TPS (-21% vs leader)
4. MySQL 8.4.8: 8,345 TPS (-22% vs leader)

**Key observations:**
- **MariaDB 11.8.6** leads by 14-28% across all MySQL and Percona variants when data is memory-resident
- **MySQL 9.7.0** shows significant improvement over 8.4.8 (+12%), closing the gap with MariaDB
- **Percona Server 8.4.8** and MySQL 8.4.8 trail behind, suggesting room for optimization in memory-bound OLTP scenarios
- All servers maintain efficient scaling up to 128 threads before experiencing lock contention degradation at 256+ threads

#### 3.1.2. I/O-Bound Workloads (2GB Buffer Pool)

**Winner: MariaDB leads significantly, but all servers experience scaling issues at high concurrency**

![I/O-Bound Table](graphs_out/table_tps_2g.png)

![I/O-Bound Performance](graphs_out/throughput_tps_2g.png)

**Top performers at 64 threads (optimal concurrency):**
1. **MariaDB 11.8.6: 4,199 TPS** - Best overall, more than doubles competition
2. Percona Server 8.4.8: 2,543 TPS (-39% vs leader)
3. MySQL 9.7.0: 2,036 TPS (-52% vs leader)
4. MySQL 8.4.8: 1,978 TPS (-53% vs leader)

**Key observations:**
- **MariaDB's substantial lead** (65-112% faster) is achieved through more aggressive I/O strategies:
  - **2.3x more read IOPS** than MySQL (105K vs 46K reads/sec) with the same 16KB page size
  - **87% NVMe utilization** vs 75-78% for competitors, indicating better I/O parallelism
  - Higher I/O wait time (48% vs 14-19%) but achieves 2x throughput by keeping NVMe busier
  - This demonstrates MariaDB's superior ability to issue parallel I/O operations under memory pressure
- **Percona Server 8.4.8** performs better than both MySQL variants in I/O-bound scenarios (+23-29%)
- **MySQL 9.7.0** shows minimal improvement over 8.4.8 (+3%) in I/O-constrained workloads, suggesting I/O optimization wasn't a focus area for this release

**Important issue: Performance cliff at 128 threads affects all servers:**
- MariaDB: 4,199 → 1,099 TPS (-74% drop)
- All servers experience significant degradation due to lock contention around undersized buffer pools
- CPU utilization collapses from 73% to 22% as threads idle waiting for buffer pool locks
- **Root cause:** Buffer pool lock contention, not storage speed. Solution is to increase buffer pool size, not enable thread pool.

#### 3.1.3. Mixed I/O Workloads (12GB Buffer Pool) - Version-Dependent Behavior

**Winners vary by concurrency level: MariaDB leads at 64 threads, MySQL 9.7.0 leads at 128 threads**

![Mixed I/O Table](graphs_out/table_tps_12g.png)

![Mixed I/O Performance](graphs_out/throughput_tps_12g.png)

**Top performers at 64 threads (optimal concurrency):**
1. **MariaDB 12.2.2: 7,364 TPS** - Best overall
2. MariaDB 11.8.6: 7,302 TPS (-1% vs leader)
3. MySQL 9.7.0: 6,924 TPS (-6% vs leader)
4. MySQL 8.4.8: 6,797 TPS (-8% vs leader)
5. Percona Server 8.4.8: 5,954 TPS (-19% vs leader)

**Top performers at 128 threads (high concurrency):**
1. **MySQL 9.7.0: 6,729 TPS** - Best at high concurrency
2. Percona Server 8.4.8: 6,619 TPS (-2% vs leader)
3. MySQL 8.4.8: 6,201 TPS (-8% vs leader)
4. **MariaDB 12.2.2: 6,080 TPS** (-10% vs leader)
5. **MariaDB 11.8.6: 3,635 TPS** (-46% vs leader) - **Significantly underperforms at this concurrency**

**Key observations:**
- **MariaDB 11.8.6 has suboptimal concurrency scaling** at 128+ threads with mixed I/O workloads (drops 50% below competition)
- **MariaDB 12.2.2 resolves this performance limitation** with 67% improvement over 11.8.6, achieving competitive performance through improved concurrent I/O handling
- **MySQL 9.7.0 excels at high concurrency** in mixed workloads, taking the lead at 128+ threads
- **Percona Server 8.4.8** maintains consistent performance but trails MariaDB at 64 threads (-19%)

#### 3.1.4. Summary across workloads

**Workload-specific observations:**

1. **Memory-resident workloads (32GB+):** 
   - **Winner: MariaDB 11.8.6** (+14-28% vs all competitors)
   - MySQL 9.7.0 is the best non-MariaDB option (+12% vs MySQL 8.4.8)

2. **I/O-bound workloads (small buffer pools):**
   - **Winner: MariaDB 11.8.6** (+65-112% vs all competitors)
   - Percona Server 8.4.8 is the best non-MariaDB option (+23-29% vs MySQL)
   - **Note:** All servers experience significant scaling issues at 128+ threads with undersized buffers

3. **Mixed I/O workloads (moderate buffer pools):**
   - **At 64 threads: MariaDB 12.2.2** (+6-19% vs all competitors)
   - **At 128+ threads: MySQL 9.7.0** leads in high-concurrency scenarios
   - **Important:** MariaDB 11.8.6 shows significantly reduced performance here - 12.2.2 has better results.

**Version-specific observations:**
- **MariaDB 11.8.6:** Shows suboptimal concurrency scaling at 128+ threads with mixed workloads. **MariaDB 12.2.2 is better** with 67% performance improvement in this scenario.
- **MySQL 8.4.8:** Consistently trails MySQL 9.7.0 by 3-12% across all workloads
- **Percona Server 8.4.8:** Strong in I/O-bound scenarios but weaker in memory-resident workloads (-21% vs MariaDB)

### 3.2. Thread Pool Findings (Secondary Experiment)

Thread pool was tested on NVMe storage but did not provide significant additional value:

**When Thread Pool Helped (Very High Oversubscription):**
- **At 512 threads with 2GB buffer:** +121% throughput (587 TPS vs 266 TPS baseline for MariaDB 11.8.6)
- **At 512 threads with 12GB buffer:** +79-83% throughput (1,285-1,302 TPS vs 704-727 TPS baseline)

Thread pool helps at very high oversubscription (512 threads) by limiting active threads to 80, reducing lock contention. However, these scenarios are unusual — normal production workloads should not operate at this level of oversubscription.

**When Thread Pool Did Not Help:**
- **Low concurrency (1-32 threads):** -3% to -20% overhead from coordination costs
- **Optimal concurrency (64-128 threads):** -3% to -10% performance penalty in most cases
- **Memory-resident workloads (32GB buffer):** Thread pool provides no benefit across all concurrency levels. Baseline achieves peak performance (~10,700 TPS) at 128 threads without thread pool

**Specific Performance Impact:**

| Memory Tier | Concurrency | Baseline | Thread Pool | Delta |
|-------------|-------------|----------|-------------|-------|
| 2GB | 64 threads | 4,199 TPS | ~4,200 TPS | 0% |
| 2GB | 128 threads | 1,099 TPS | 657 TPS | -40% |
| 12GB | 64 threads | 7,302 TPS | 7,119 TPS | -3% |
| 12GB | 128 threads (11.8.6) | 3,635 TPS | 4,234 TPS | +16% |
| 12GB | 128 threads (12.2.2) | 6,080 TPS | 5,455 TPS | -10% |
| 32GB | 128 threads | 10,694 TPS | 10,232 TPS | -4% |

**Possible improvements:**
1. **For I/O-bound workloads:** Increase buffer pool size rather than enabling thread pool — the 2GB configuration's performance cliff is due to buffer pool lock contention, which thread pool cannot solve effectively
2. **For mixed I/O workloads:** Upgrade to MariaDB 12.2.2 first (67% better than 11.8.6 at 128 threads). Only enable thread pool if regularly operating at 256+ concurrent connections
3. **For memory-resident workloads:** Skip thread pool entirely. Focus on lock optimization and query tuning instead

## 4. Test Environment & Infrastructure

### 4.1. Hardware Specification

#### System Information

- **Platform**: Linux
- **Release**: Ubuntu 24.04 LTS (noble)
- **Kernel**: 6.8.0-60-generic
- **Architecture**: CPU = 64-bit, OS = 64-bit
- **Virtualized**: No virtualization detected

#### CPU

- **Architecture**: x86_64
- **CPU op-mode(s)**: 32-bit, 64-bit
- **Byte Order**: Little Endian
- **Processors**: physical = 2, cores = 40, virtual = 80, hyperthreading = yes
- **Sockets**: 2
- **Cores per socket**: 20
- **Threads per core**: 2
- **Model**: 80x Intel(R) Xeon(R) Gold 6230 CPU @ 2.10GHz
- **Base Frequency**: 2.10GHz
- **Max Frequency**: 3.90GHz
- **Cache**: 80x 28160 KB

#### NUMA

- **NUMA Nodes**: 2
- **Node 0**: 95288 MB (CPUs: 0-19, 40-59)
- **Node 1**: 96748 MB (CPUs: 20-39, 60-79)

#### Memory

- **Total Memory**: 187.5G
- **Swap Size**: 8.0G

#### Storage Configuration

**Primary Storage (SDA - System Disk)**
- **Device**: /dev/sda
- **Total Size**: 894.3 GB
- **Filesystem**: ext4

**Secondary Storage (NVMe)**
- **Device**: /dev/nvme0n1
- **Total Size**: 2.9 TB
- **Filesystem**: ext4

### 4.2. Software Configuration

#### Operating System

- **Distribution**: Ubuntu 24.04 LTS (noble)
- **Kernel**: 6.8.0-60-generic
- **Architecture**: 64-bit

#### Containerization

- **Docker**: Used for database server deployment
- **Network Mode**: `--network host` (native host networking, no NAT overhead)

#### Benchmark Tool

- **Sysbench**: Version 1.0.20
- **LuaJIT**: 2.1.0-beta3 (system)
- **Test Script**: OLTP Read-Write (built-in)

#### Telemetry Tools

System performance metrics were collected continuously during each benchmark run:

- **iostat**: I/O statistics monitoring
- **vmstat**: Virtual memory and system statistics
- **mpstat**: Multi-processor statistics
- **dstat**: Combined system resource statistics
- **Sampling Interval**: 1 second for all tools
- **Collection Period**: Full duration of each 15-minute test run

### 4.3. Containerization Strategy

Each MariaDB engine was run as a Docker container using official images from the `mariadb` repository. The host network mode was used to avoid bridge networking overhead. A fresh container was started for each engine/tier combination using the following sequence:

1. **Stop and remove** any existing benchmark container
2. **Detect actual server version** by connecting and running `SELECT VERSION()`
3. **Generate a version-specific configuration file** (see Section 3)
4. **Restart the container** with the new configuration mounted
5. **Wait for the server to become ready** (mariadb-admin ping loop)
6. **Verify InnoDB buffer pool size** matches the intended tier (hard abort on mismatch)

This approach ensured that each test run started with a clean state and the correct configuration parameters were applied before benchmark execution.

### 4.4. Buffer Pool Tiers

With the database size of 24 GB, three InnoDB buffer pool sizes were tested, each representing a distinct workload characteristic:

| Tier (innodb_buffer_pool_size) | Workload Character |
|---------------------------------|--------------------|
| **2 GB** | **I/O bound** — dataset substantially exceeds buffer pool (1:12 ratio); heavy read amplification |
| **12 GB** | **Mixed** — partial dataset fits in memory (1:2 ratio); realistic production scenario |
| **32 GB** | **In-memory** — full working set fits; CPU and locking are primary bottlenecks |

These tiers were selected to evaluate MariaDB performance across different memory pressure scenarios, from heavily disk-constrained (2 GB) to fully memory-resident (32 GB) workloads.

## 5. Database Configuration

All database servers were configured with production-grade settings optimized for OLTP workloads. InnoDB I/O parameters were tuned for NVMe storage to utilize its low latency and high throughput capabilities.

### 5.1. General Settings

```
performance_schema              = OFF
skip-name-resolve               = ON
max_connections                 = 2000
max_connect_errors              = 1000000
max_prepared_stmt_count         = 1000000
```

### 5.2. Thread Handling

**Thread Pool Configuration (mariadb-thp servers):**
```
thread_handling                 = pool-of-threads
thread_pool_size                = 80                # match physical core count
thread_pool_max_threads         = 2000
thread_stack                    = 512K
thread_cache_size               = 256
back_log                        = 4096
```

**Default Configuration (mariadb servers):**
```
thread_handling                 = one-thread-per-connection
thread_cache_size               = 256
thread_stack                    = 512K
back_log                        = 4096
```

### 5.3. InnoDB Buffer Pool

Buffer pool size varied by tier (see Section 3.4):
```
innodb_buffer_pool_size         = 2G | 12G | 32G
```

### 5.4. InnoDB I/O Configuration

Optimized for NVMe storage with high concurrency:
```
innodb_io_capacity              = 10000
innodb_io_capacity_max          = 20000
innodb_read_io_threads          = 16
innodb_write_io_threads         = 16
innodb_use_native_aio           = ON
```

### 5.5. InnoDB Durability & Logging

Full ACID compliance with transaction log optimization:
```
innodb_log_file_size            = 4G
innodb_log_buffer_size          = 256M
innodb_flush_log_at_trx_commit  = 1                 # full ACID
innodb_doublewrite              = ON
sync_binlog                     = 1
```

### 5.6. InnoDB Concurrency & OLTP Tuning

```
innodb_stats_on_metadata        = OFF
innodb_open_files               = 65536
innodb_lock_wait_timeout        = 50
innodb_rollback_on_timeout      = ON
innodb_snapshot_isolation       = OFF               # MariaDB 12.x+
```

### 5.7. Per-Session Buffers

Conservative settings to support high connection counts:
```
sort_buffer_size                = 4M
join_buffer_size                = 4M
read_buffer_size                = 2M
read_rnd_buffer_size            = 4M
tmp_table_size                  = 256M
max_heap_table_size             = 256M
```

### 5.8. Table & File Handles

```
table_open_cache                = 65536
table_definition_cache          = 65536
open_files_limit                = 1000000
table_open_cache_instances      = 64
```

### 5.9. Binary Logging

Enabled for production-realistic overhead measurement:
```
log_bin                         = /var/lib/mysql/mysql-bin
binlog_format                   = ROW
binlog_row_image                = MINIMAL
binlog_cache_size               = 4M
max_binlog_size                 = 512M
```

**Note:** The complete configuration file is available in the benchmark logs directory as `TierXG.cnf.txt` for each tested configuration.

## 6. Benchmark Workload

### 6.1. Warmup Protocol

Before each production benchmark run, the database underwent a two-phase warmup sequence to ensure consistent starting conditions:

| Phase | Duration | Purpose |
|-------|----------|---------|
| **Warmup A — Read-Only** | 180 s (3 min) | Populate buffer pool with hot pages |
| **Warmup B — Read-Write** | 600 s (10 min) | Steady-state redo log & dirty page ratio (skipped for RO) |

**Note:** The proposed warmup values are determined experimentally and are sufficient for the hardware configuration used for the benchmarking. However, in case of much slower hosts the user will need to adjust them by editing scripts.

### 6.2. Measurement Run

Following the warmup phase, each benchmark execution ran for **900 seconds (15 minutes)** with performance metrics captured at 1-second granularity. During execution, system-level telemetry tools (iostat, vmstat, mpstat, dstat) collected resource utilization data in parallel.

#### Data Collection Strategy

The results presented in this report represent a **single measurement per configuration**. To validate result stability and confirm steady-state operation, we conducted selective repeat runs (2nd and 3rd iterations) across representative server and memory tier combinations. These validation runs consistently confirmed the reproducibility of the initial measurements.

The validation dataset was intentionally excluded from publication to maintain data accessibility. Given that each baseline measurement produces multiple output files (sysbench results, iostat, vmstat, mpstat, dstat, and configuration logs), the inclusion of validation runs would have multiplied the dataset size significantly, creating an unwieldy collection of thousands of files that would be difficult to navigate and distribute.

#### Steady-State Verification

**Read Operations:** Steady state for read workloads was verified by monitoring InnoDB buffer pool metrics and OS-level I/O read counters. The system was considered stable when physical reads dropped to near-zero after the warmup period, indicating the working set was fully cached.

**Write Operations:** For write-intensive phases, stability was determined by observing transaction throughput and latency metrics until they reached consistent values without significant drift.

**Known Limitation:** While short-term metric stability (15 minutes) provides confidence in measurement consistency, it does not entirely eliminate the possibility of longer-term background activity such as adaptive flushing, change buffer merges, or checkpoint behavior that might emerge during extended multi-day operations. The chosen measurement window represents a balance between statistical confidence and practical benchmarking constraints.

## 7. Metrics & Reporting

### 7.1. Primary Metrics

| Metric | Definition |
|--------|------------|
| **TPS** | Transactions per second (complete BEGIN/COMMIT cycles) |

### 7.2. Derived Metrics

Performance analysis includes:
- **TPS gain relative to additional RAM**: Throughput improvement when increasing `innodb_buffer_pool_size` from one tier to another
- **TPS gain relative to thread count increase**: Scalability characteristics as concurrent client connections grow

### 7.3. Output Files

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

## 8. Limitations and Considerations

This benchmark provides valuable performance insights but operates under specific constraints that should be considered when interpreting results:

**Single-Host Architecture:**
- All measurements reflect single-node performance only
- Replication topologies, cluster configurations, and proxy layers introduce additional overhead not captured in these tests
- Network latency and multi-node coordination costs are not represented in these results

**Synthetic Workload Characteristics:**
- The sysbench oltp_read_write workload provides a standardized OLTP approximation but does not capture the complexity of real application query patterns
- Actual production workloads exhibit varying query distributions, transaction sizes, and access patterns
- Results should be interpreted as directional indicators rather than absolute predictions of production performance

**Data Distribution Patterns:**
- Benchmark uses uniformly distributed random data access across the entire dataset
- Real-world applications typically exhibit non-uniform access patterns (hot rows, temporal locality, geographic clustering)
- Cache hit rates and I/O patterns may differ significantly in production environments with skewed data access

**Dataset Size Constraints:**
- 24GB working set is representative of small to medium database sizes
- Enterprise databases often operate at much larger scales (hundreds of GB to TB range)
- Larger datasets may exhibit different performance characteristics, particularly regarding buffer pool efficiency and I/O patterns

**Controlled Environment:**
- Tests run on dedicated hardware with minimal background processes
- Production environments experience variable load patterns, competing workloads, and system maintenance activities
- Real-world performance may be affected by factors not present in this controlled benchmark environment

These limitations do not diminish the value of the findings but provide important context for applying these results to production scenarios. The relative performance differences observed between configurations remain instructive even as absolute numbers may vary in different deployment contexts.

## 9. Reproducibility

This benchmark is designed to be reproducible on compatible systems. The testing framework and automation scripts are available in the project repository.

**System Requirements:**

**Operating System:**
- Ubuntu 24.04 LTS (current supported platform)
- Other Linux distributions may work but are not officially tested

**Software Prerequisites:**

Install required packages:
```
sudo apt install docker.io sysstat sysbench mysql-client dstat -y
```

**Docker Group Permissions:**

Add your user to the docker group to run containers without sudo:
```
sudo usermod -aG docker $USER
```

After running this command, log out and back in, or run `newgrp docker` to activate the new group membership without restarting your session.

**Root Access Requirement:**

The benchmark scripts require sudo privileges for:
- CPU frequency governor configuration (`cpupower`)
- System telemetry collection (iostat, vmstat, mpstat, dstat)
- Configuration file management

Your user account must have sudo access to run the benchmark suite.

**Running the Benchmarks:**

The repository includes automated scripts for running the complete benchmark suite:

**Full benchmark suite** (both thread pool configurations):
```
./run_all.sh
```

This script automatically:
- Installs additional dependencies
- Runs system profiling tools
- Executes benchmarks for MariaDB 11.8.6 and 12.2.2
- Tests both default (one-thread-per-connection) and thread pool configurations
- Generates separate result directories for each configuration

**Hardware Considerations:**

While the benchmark can run on various hardware configurations, results will vary significantly based on:
- CPU core count (affects thread pool sizing and concurrency behavior)
- Available RAM (determines realistic buffer pool tiers)
- Storage performance (critical for I/O-bound workloads)

The thread pool size in the default configuration is set to 80 threads to match the 80-thread (40 physical core) test system. Adjust `thread_pool_size` in `run_metrics.sh` to match your system's physical core count for optimal results.
