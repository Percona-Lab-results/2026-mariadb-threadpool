# MariaDB OLTP Performance: Storage Upgrade and Configuration Optimization Study

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

The [previous benchmark study](https://www.percona.com/blog/2026-mysql-ecosystem-performance-benchmark-report/) ran MariaDB 11.4.10 and 12.1.2 on **SATA SSD storage** with conservative I/O settings (`innodb_io_capacity=2500`).

This benchmark study evaluates the performance impact of the following changes:

- **NVMe storage** instead of SATA SSD (**PRIMARY improvement factor**)
- **Aggressive I/O tuning** to match NVMe capabilities (`innodb_io_capacity=10000`, 16 I/O threads)
- **Updated MariaDB versions** (11.8.6 and 12.2.2)
- **Thread pool testing** as a secondary experiment

The goal is to quantify the performance gain from SATA SSD → NVMe migration with proper configuration tuning, and whether thread pool provides additional value in this environment.

### Target Questions

This analysis seeks to answer the following key questions:

1. **Storage Hardware Impact**
   - How much did migrating from SATA SSD to NVMe improve throughput?
   - What is the delta in I/O-bound (2GB buffer) vs memory-resident (32GB buffer) workloads?
   - How much of the improvement comes from hardware vs configuration tuning?

2. **Version Upgrade Impact**
   - How do MariaDB 11.8.6 and 12.2.2 compare to their predecessors (11.4.10, 12.1.2)?
   - Which version upgrades provided the most significant improvements?
   - Are there concurrency levels where version differences are most visible?

3. **Before/After Performance Delta**
   - At which concurrency and memory tier combinations did we see the largest improvements?
   - Did the NVMe migration shift the performance curve or just raise the ceiling?
   - What workload characteristics benefited most from faster storage?

4. **Thread Pool as Secondary Experiment**
   - Does thread pool provide additional value on top of NVMe storage?
   - Are the thread pool benefits observed with fast storage consistent with expectations?
   - When would thread pool be recommended given NVMe baseline performance?

### Scope

- **Primary Comparison**: Previous run (SATA SSD, MariaDB 11.4.10/12.1.2, innodb_io_capacity=2500) vs Current run (NVMe, MariaDB 11.8.6/12.2.2, innodb_io_capacity=10000)
- **Secondary Test**: Thread Pool configuration (with and without) on NVMe storage
- **Reference Systems**: MySQL 8.4.8, MySQL 9.7.0-er2, Percona Server 8.4.8 (for comparative context)
- **Workload Type**: Sysbench OLTP Read-Write
- **Concurrency Levels**: 1, 4, 16, 32, 64, 128, 256, 512 client threads
- **Memory Tiers**: 2 GB, 12 GB, 32 GB `innodb_buffer_pool_size`
- **Thread Pool Configuration**: `thread_pool_size=80`, `thread_pool_max_threads=2000`

### 2.2. Configurations Under Test

**Previous Run (baseline for comparison):**
- **Storage:** SATA SSD
- MariaDB 11.4.10 with `innodb_io_capacity=2500`
- MariaDB 12.1.2 with `innodb_io_capacity=2500`

**Current Run (NVMe migration):**

| Server | Version | Storage | I/O Config | Thread Handling | Role |
|--------|---------|---------|-----------|----------------|------|
| **MariaDB** | 11.8.6 | NVMe | innodb_io_capacity=10000, 16 threads | Default | Primary: NVMe + version delta |
| **MariaDB** | 11.8.6 | NVMe | innodb_io_capacity=10000, 16 threads | Thread Pool | Secondary: thread pool test |
| **MariaDB** | 12.2.2 | NVMe | innodb_io_capacity=10000, 16 threads | Default | Primary: NVMe + version delta |
| **MariaDB** | 12.2.2 | NVMe | innodb_io_capacity=10000, 16 threads | Thread Pool | Secondary: thread pool test |
| **MySQL** | 8.4.8 | NVMe | innodb_io_capacity=10000, 16 threads | Default | Reference |
| **MySQL** | 9.7.0-er2 | NVMe | innodb_io_capacity=10000, 16 threads | Default | Reference |
| **Percona Server** | 8.4.8-8 | NVMe | innodb_io_capacity=10000, 16 threads | Default | Reference |

**Key Changes from Previous Run:**
- **Storage:** SATA SSD → **NVMe** (PRIMARY factor)
- `innodb_io_capacity`: 2500 → 10000 (tuned for NVMe)
- `innodb_io_capacity_max`: 5000 → 20000 (tuned for NVMe)
- `innodb_read_io_threads`: 4 → 16 (tuned for NVMe)
- `innodb_write_io_threads`: 4 → 16 (tuned for NVMe)
- MariaDB versions: 11.4.10 → 11.8.6, 12.1.2 → 12.2.2

## 3. Key Findings

This section summarizes the critical performance insights derived from comparing the tuned configuration against the previous baseline, plus observations from the thread pool experiment.

### 3.1. NVMe Storage Migration Impact (Primary Finding)

Migrating from SATA SSD to NVMe storage (with appropriate I/O configuration tuning) provided dramatic improvements:

**MariaDB 11 Series (11.4.10 SATA → 11.8.6 NVMe):**

| Buffer Pool | Concurrency | Old (SATA SSD) | New (NVMe) | Improvement | Key Insight |
|-------------|-------------|----------------|------------|-------------|-------------|
| **2 GB (I/O bound)** | 64 threads | 614 TPS | 4,199 TPS | **+584% (6.8x)** | NVMe eliminates SATA bottleneck |
| **12 GB (Mixed)** | 128 threads | 1,212 TPS | 3,635 TPS | **+200% (3x)** | Partial I/O pressure still shows major gains |
| **32 GB (Memory)** | 128 threads | 10,232 TPS | 10,694 TPS | **+5%** | Minimal storage impact when fully cached |

**MariaDB 12 Series (12.1.2 SATA → 12.2.2 NVMe):**

| Buffer Pool | Concurrency | Old (SATA SSD) | New (NVMe) | Improvement | Key Insight |
|-------------|-------------|----------------|------------|-------------|-------------|
| **2 GB (I/O bound)** | 64 threads | 614 TPS | 4,186 TPS | **+582% (6.8x)** | NVMe eliminates SATA bottleneck |
| **12 GB (Mixed)** | 128 threads | 1,216 TPS | 6,081 TPS | **+400% (5x)** | MariaDB 12.2.2 uses NVMe better at high concurrency |
| **32 GB (Memory)** | 128 threads | 10,273 TPS | 17,710 TPS | **+72%** | Version upgrade contributes significant gains even when memory-resident |

**Important Note:** MariaDB 12.2.2 shows substantially stronger improvements than 11.8.6, particularly in memory-resident workloads. The 72% gain at 32GB (vs 11.8.6's 5%) suggests that the 12.1.2 → 12.2.2 upgrade included architectural improvements beyond just I/O handling, possibly in lock contention or transaction processing efficiency.

**Key Observation:** 

The previous benchmark on **SATA SSD storage** was severely bottlenecked by storage I/O. At 64 threads with 2GB buffer (heavy I/O workload), SATA could only deliver ~614 TPS. **NVMe storage delivers 6.8x higher throughput** at the same concurrency level.

The improvement is most dramatic in I/O-bound scenarios (2GB buffer) and diminishes as workloads become more memory-resident (32GB buffer, only 5% gain). This confirms that the previous configuration was storage-constrained, not CPU or lock-constrained.

### 3.2. Version Upgrade Impact

**MariaDB 11.4.10 → 11.8.6:**

The version upgrade itself provides minimal delta — the massive improvements shown in section 3.1 are primarily driven by the SATA → NVMe storage migration. At memory-resident workloads where storage speed has minimal impact:
- 32GB buffer, 128 threads: 10,232 TPS → 10,694 TPS (+5%)

This suggests the 11.4.10 → 11.8.6 upgrade provides incremental improvements but is not the primary performance driver.

**MariaDB 12.1.2 → 12.2.2:**

Version 12.2.2 demonstrates architectural improvements in concurrent I/O handling that better utilize NVMe capabilities:
- At 128 threads/12GB (mixed I/O): maintains 43% CPU utilization vs 11.8.6's 11%
- Prevents I/O serialization that affects 11.8.6 at this concurrency level
- 67% higher throughput than 11.8.6 at 128 threads/12GB (6,080 vs 3,635 TPS)
- Sustains 1.77 GB/s disk read bandwidth vs 11.8.6's 541 MB/s

The 12.x series has better I/O queue management and can fully utilize NVMe's high concurrency capabilities more effectively than 11.x.

**Combined Effect:** 

For I/O-bound workloads, the aggregate improvement is dominated by the NVMe migration (contributing ~580% of the gain). However, **MariaDB 12.2.2 provides substantial additional benefits**:
- **I/O-bound (2GB):** ~6.8x from NVMe (version contribution minimal)
- **Mixed I/O (12GB):** ~5x total (NVMe + improved I/O queue management in 12.2.2)
- **Memory-resident (32GB):** ~72% gain despite no I/O bottleneck (architectural improvements in 12.2.2)

The 12.1.2 → 12.2.2 upgrade appears to include significant improvements beyond just I/O handling, potentially in lock management, transaction processing, or CPU efficiency, as evidenced by the 72% gain in fully memory-resident workloads where storage speed is irrelevant.

### 3.3. Thread Pool Findings (Secondary Experiment)

Thread pool was tested on NVMe storage but did not provide additional value beyond the storage upgrade:

**When Thread Pool Helped (High Concurrency):**
- At 512 threads with 2GB buffer: +121-143% throughput (587-600 TPS vs 247-266 TPS baseline)
- At 512 threads with 12GB buffer: +79-83% throughput (1,285-1,302 TPS vs 704-727 TPS baseline)

**When Thread Pool Did Not Help:**
- Low concurrency (1-32 threads): 3-10% overhead from coordination costs
- Memory-resident workloads (32GB buffer): minimal benefit, baseline already handles 128 threads efficiently
- Peak performance point (128 threads, 32GB): baseline achieves ~10,600 TPS, thread pool provides no additional gain

**Why Thread Pool Wasn't Needed Here:**

NVMe storage already eliminated the bottlenecks that thread pool typically addresses:
- NVMe's low latency and high concurrent I/O capability handle high concurrency without thread thrashing
- The previous run on SATA SSD likely would have benefited more from thread pool
- Thread pool value proposition is strongest when storage is slow or undersized for the workload

### 3.4. Practical Recommendations

**Priority 1: Migrate to NVMe Storage**
- **6-7x performance improvement** for I/O-bound workloads
- Essential for high-concurrency OLTP applications with datasets exceeding buffer pool
- Configure InnoDB appropriately: `innodb_io_capacity=10000`, 16 I/O threads for NVMe

**Priority 2: Upgrade to Latest MariaDB Versions**
- MariaDB 12.2.2 shows superior concurrent I/O handling that better utilizes NVMe
- Version upgrades are particularly valuable for mixed I/O workloads (partial buffer pool coverage)
- 67% higher throughput than 11.8.6 at high concurrency on NVMe

**Priority 3: Consider Thread Pool Only If...**
- You regularly see connection counts exceeding 256+ concurrent threads
- You have I/O-bound workloads where dataset significantly exceeds buffer pool
- Your environment has unpredictable connection spikes requiring stability

**Not Recommended:**
- Enabling thread pool without first migrating to NVMe (fix the root cause first)
- Thread pool for workloads operating at <128 concurrent connections
- Thread pool for fully memory-resident datasets with predictable concurrency
- Staying on SATA SSD for I/O-intensive database workloads

## 4. Before/After Comparison Summary

This section directly compares the previous run (SATA SSD) against the current run (NVMe + version updates) to highlight the improvement.

### 4.1. Configuration Comparison

| Parameter | Previous Run | Current Run | Change |
|-----------|-------------|-------------|---------|
| **Storage Hardware** | **SATA SSD** | **NVMe** | **PRIMARY CHANGE** |
| MariaDB 11.x | 11.4.10 | 11.8.6 | +2 minor versions |
| MariaDB 12.x | 12.1.2 | 12.2.2 | +1 minor version |
| innodb_io_capacity | 2500 | 10000 | **4x** (tuned for NVMe) |
| innodb_io_capacity_max | 5000 | 20000 | **4x** (tuned for NVMe) |
| innodb_read_io_threads | 4 | 16 | **4x** (tuned for NVMe) |
| innodb_write_io_threads | 4 | 16 | **4x** (tuned for NVMe) |

### 4.2. Performance Delta (MariaDB 11.x Series)

Selected representative concurrency and memory tier combinations showing the impact:

| Test Scenario | Old (SATA SSD) | New (NVMe) | Improvement | Analysis |
|---------------|----------------|------------|-------------|----------|
| **2GB, 64 threads** | 614 TPS | 4,199 TPS | **+584% (6.8x)** | SATA bottleneck eliminated by NVMe |
| **12GB, 128 threads** | 1,212 TPS | 3,635 TPS | **+200% (3x)** | Mixed workload benefits substantially |
| **32GB, 128 threads** | 10,232 TPS | 10,694 TPS | **+5%** | Memory-resident: minimal storage impact |

**Key Takeaway:** The improvement is inversely proportional to buffer pool size. Heavy I/O workloads (2GB buffer) see 6-7x gains from NVMe, while memory-resident workloads (32GB buffer) see minimal improvement, confirming the previous configuration was SATA storage-constrained.

### 4.3. What Changed

The previous run on SATA SSD showed I/O serialization at moderate-to-high concurrency. The telemetry revealed:
- SATA latency and throughput limits causing queue depth bottlenecks
- Context switching overhead while waiting for slow SATA I/O
- Threads idling on I/O wait instead of performing productive work

**The Root Cause:** SATA SSD has inherent latency (~100-200μs) and limited concurrent I/O capability compared to NVMe (~10-20μs latency, much higher queue depth).

**The Fix:** Migrating to NVMe storage provided:
- **10-20x lower latency** per I/O operation
- **Higher concurrent I/O throughput** (NVMe can handle 10,000+ IOPS easily)
- **Better queue depth handling** for high-concurrency workloads

The I/O configuration changes (`innodb_io_capacity=10000`, 16 threads) were necessary to allow InnoDB to fully utilize NVMe's capabilities, but the hardware migration was the primary improvement factor.

## 5. Test Environment & Infrastructure

### 5.1. Hardware Specification

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

### 8.2. Software Configuration

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

### 6.3. Containerization Strategy

Each MariaDB engine was run as a Docker container using official images from the `mariadb` repository. The host network mode was used to avoid bridge networking overhead. A fresh container was started for each engine/tier combination using the following sequence:

1. **Stop and remove** any existing benchmark container
2. **Detect actual server version** by connecting and running `SELECT VERSION()`
3. **Generate a version-specific configuration file** (see Section 3)
4. **Restart the container** with the new configuration mounted
5. **Wait for the server to become ready** (mariadb-admin ping loop)
6. **Verify InnoDB buffer pool size** matches the intended tier (hard abort on mismatch)

This approach ensured that each test run started with a clean state and the correct configuration parameters were applied before benchmark execution.

### 6.4. Buffer Pool Tiers

With the database size of 24 GB, three InnoDB buffer pool sizes were tested, each representing a distinct workload characteristic:

| Tier (innodb_buffer_pool_size) | Workload Character |
|---------------------------------|--------------------|
| **2 GB** | **I/O bound** — dataset substantially exceeds buffer pool (1:12 ratio); heavy read amplification |
| **12 GB** | **Mixed** — partial dataset fits in memory (1:2 ratio); realistic production scenario |
| **32 GB** | **In-memory** — full working set fits; CPU and locking are primary bottlenecks |

These tiers were selected to evaluate MariaDB performance across different memory pressure scenarios, from heavily disk-constrained (2 GB) to fully memory-resident (32 GB) workloads.

## 6. Database Configuration

All MariaDB servers were configured with production-grade settings optimized for OLTP workloads. The configuration below represents the current (NVMe) run; the previous run on SATA SSD used identical settings except for I/O parameters.

**Key Changes from Previous Run (SATA SSD → NVMe):**
- **Storage Hardware:** SATA SSD → **NVMe** (PRIMARY factor in 6-7x improvement)
- `innodb_io_capacity`: 2500 → **10000** (tuned for NVMe)
- `innodb_io_capacity_max`: 5000 → **20000** (tuned for NVMe)
- `innodb_read_io_threads`: 4 → **16** (tuned for NVMe)
- `innodb_write_io_threads`: 4 → **16** (tuned for NVMe)

The I/O configuration changes are essential to utilize NVMe's low latency and high throughput capabilities (see Section 3.1).

### 6.1. General Settings

```
performance_schema              = OFF
skip-name-resolve               = ON
max_connections                 = 2000
max_connect_errors              = 1000000
max_prepared_stmt_count         = 1000000
```

### 8.2. Thread Handling

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

### 6.3. InnoDB Buffer Pool

Buffer pool size varied by tier (see Section 3.4):
```
innodb_buffer_pool_size         = 2G | 12G | 32G
```

### 6.4. InnoDB I/O Configuration

Optimized for NVMe storage with high concurrency:
```
innodb_io_capacity              = 10000
innodb_io_capacity_max          = 20000
innodb_read_io_threads          = 16
innodb_write_io_threads         = 16
innodb_use_native_aio           = ON
```

### 6.5. InnoDB Durability & Logging

Full ACID compliance with transaction log optimization:
```
innodb_log_file_size            = 4G
innodb_log_buffer_size          = 256M
innodb_flush_log_at_trx_commit  = 1                 # full ACID
innodb_doublewrite              = ON
sync_binlog                     = 1
```

### 6.6. InnoDB Concurrency & OLTP Tuning

```
innodb_stats_on_metadata        = OFF
innodb_open_files               = 65536
innodb_lock_wait_timeout        = 50
innodb_rollback_on_timeout      = ON
innodb_snapshot_isolation       = OFF               # MariaDB 12.x+
```

### 6.7. Per-Session Buffers

Conservative settings to support high connection counts:
```
sort_buffer_size                = 4M
join_buffer_size                = 4M
read_buffer_size                = 2M
read_rnd_buffer_size            = 4M
tmp_table_size                  = 256M
max_heap_table_size             = 256M
```

### 6.8. Table & File Handles

```
table_open_cache                = 65536
table_definition_cache          = 65536
open_files_limit                = 1000000
table_open_cache_instances      = 64
```

### 6.9. Binary Logging

Enabled for production-realistic overhead measurement:
```
log_bin                         = /var/lib/mysql/mysql-bin
binlog_format                   = ROW
binlog_row_image                = MINIMAL
binlog_cache_size               = 4M
max_binlog_size                 = 512M
```

**Note:** The complete configuration file is available in the benchmark logs directory as `TierXG.cnf.txt` for each tested configuration.

## 7. Benchmark Workload

### 8.1. Warmup Protocol

Before each production benchmark run, the database underwent a two-phase warmup sequence to ensure consistent starting conditions:

| Phase | Duration | Purpose |
|-------|----------|---------|
| **Warmup A — Read-Only** | 180 s (3 min) | Populate buffer pool with hot pages |
| **Warmup B — Read-Write** | 600 s (10 min) | Steady-state redo log & dirty page ratio (skipped for RO) |

**Note:** The proposed warmup values are determined experimentally and are sufficient for the hardware configuration used for the benchmarking. However, in case of much slower hosts the user will need to adjust them by editing scripts.

### 8.2. Measurement Run

Following the warmup phase, each benchmark execution ran for **900 seconds (15 minutes)** with performance metrics captured at 1-second granularity. During execution, system-level telemetry tools (iostat, vmstat, mpstat, dstat) collected resource utilization data in parallel.

#### Data Collection Strategy

The results presented in this report represent a **single measurement per configuration**. To validate result stability and confirm steady-state operation, we conducted selective repeat runs (2nd and 3rd iterations) across representative server and memory tier combinations. These validation runs consistently confirmed the reproducibility of the initial measurements.

The validation dataset was intentionally excluded from publication to maintain data accessibility. Given that each baseline measurement produces multiple output files (sysbench results, iostat, vmstat, mpstat, dstat, and configuration logs), the inclusion of validation runs would have multiplied the dataset size significantly, creating an unwieldy collection of thousands of files that would be difficult to navigate and distribute.

#### Steady-State Verification

**Read Operations:** Steady state for read workloads was verified by monitoring InnoDB buffer pool metrics and OS-level I/O read counters. The system was considered stable when physical reads dropped to near-zero after the warmup period, indicating the working set was fully cached.

**Write Operations:** For write-intensive phases, stability was determined by observing transaction throughput and latency metrics until they reached consistent values without significant drift.

**Known Limitation:** While short-term metric stability (15 minutes) provides confidence in measurement consistency, it does not entirely eliminate the possibility of longer-term background activity such as adaptive flushing, change buffer merges, or checkpoint behavior that might emerge during extended multi-day operations. The chosen measurement window represents a balance between statistical confidence and practical benchmarking constraints.

## 8. Metrics & Reporting

### 8.1. Primary Metrics

| Metric | Definition |
|--------|------------|
| **TPS** | Transactions per second (complete BEGIN/COMMIT cycles) |

### 8.2. Derived Metrics

Performance analysis includes:
- **TPS gain relative to additional RAM**: Throughput improvement when increasing `innodb_buffer_pool_size` from one tier to another
- **TPS gain relative to thread count increase**: Scalability characteristics as concurrent client connections grow

### 8.3. Output Files

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

## 9. Measurement Results

This section presents throughput measurements from the current (tuned) run. The tables and graphs show MariaDB 11.8.6 and 12.2.2 with the optimized I/O configuration. For before/after comparisons against the previous run (MariaDB 11.4.10 and 12.1.2 with `innodb_io_capacity=2500`), refer to Section 3.1.

**Organization:**
- Results are grouped by memory tier (2GB, 12GB, 32GB)
- Each tier includes performance tables, graphs, and brief thread pool analysis
- Thread pool analysis is secondary — the primary story is the I/O configuration improvement

**Reading the Results:**
- Color-coded bars show relative performance within each memory tier
- MariaDB versions ending in "-thp" indicate thread pool enabled
- Focus on the baseline (non-thread-pool) results to understand the I/O tuning impact

### 9.1. Performance Summary Tables

The following tables show TPS (Transactions Per Second) values for each configuration. Color coding indicates relative performance within each memory tier:
- **Green bars**: High performance relative to other configurations at the same thread count
- **Yellow/Orange bars**: Mid-range performance
- **Red bars**: Lower performance relative to other configurations

Bar length is proportional to the actual value relative to the maximum in each column, making it easy to visually compare performance across different servers at the same concurrency level.

### 9.2. 2GB Buffer Pool Results

#### 9.2.1. Performance Table

![TPS Table - 2GB Buffer Pool](graphs_out/table_tps_2g.png)

#### 9.2.2. Throughput Graph

![TPS Graph - 2GB Buffer Pool](graphs_out/throughput_tps_2g.png)

#### 9.2.3. Thread Pool Analysis (2GB - I/O Bound)

*Note: This is a secondary experiment. The primary performance improvement came from migrating to NVMe storage (see Section 3.1).*

**Thread Pool Effect Summary:**

| Concurrency | Baseline | Thread Pool | Delta | Interpretation |
|-------------|----------|-------------|-------|----------------|
| 1-16 threads | 142 TPS | 138 TPS | -3% | Minor overhead at low concurrency |
| 64 threads | 4,199 TPS | ~4,200 TPS | 0% | Performance parity |
| 128 threads | 1,099 TPS | 657 TPS | -40% | Performance cliff still visible |
| 512 threads | 266 TPS | 587 TPS | **+121%** | Thread pool prevents extreme thrashing |

**Key Observation:**

Despite NVMe storage, the baseline configuration still experiences a severe performance cliff at 128 threads (4,199 → 1,099 TPS, -74% drop). System metrics show this is due to lock contention around the undersized 2GB buffer pool, not storage speed:
- CPU drops from 73% active (64 threads) to 22% active (128 threads)
- I/O bandwidth collapses from 1,648 MB/s to 410 MB/s despite low NVMe utilization
- Threads idle waiting for buffer pool locks rather than performing productive I/O

Thread pool helps at extreme oversubscription (512 threads) by limiting active threads to 80, reducing lock contention. However, the better solution is to **increase buffer pool size** rather than adding thread pool — the 12GB and 32GB configurations don't exhibit this pathology.

### 9.3. 12GB Buffer Pool Results

#### 9.3.1. Performance Table

![TPS Table - 12GB Buffer Pool](graphs_out/table_tps_12g.png)

#### 9.3.2. Throughput Graph

![TPS Graph - 12GB Buffer Pool](graphs_out/throughput_tps_12g.png)

#### 9.3.3. Thread Pool Analysis (12GB - Mixed Workload)

*Note: This is a secondary experiment. The primary performance improvement came from migrating to NVMe storage (see Section 3.1).*

**Thread Pool Effect Summary:**

| Concurrency | Baseline (11.8.6) | Thread Pool | Delta | Baseline (12.2.2) | Thread Pool | Delta |
|-------------|-------------------|-------------|-------|-------------------|-------------|-------|
| 1-16 threads | 226 TPS | 215 TPS | -5% | 226 TPS | 213 TPS | -6% |
| 64 threads | 7,302 TPS | 7,119 TPS | -3% | 7,364 TPS | 7,143 TPS | -3% |
| 128 threads | 3,635 TPS | 4,234 TPS | +16% | 6,080 TPS | 5,455 TPS | -10% |
| 512 threads | 727 TPS | 1,302 TPS | **+79%** | 704 TPS | 1,285 TPS | **+83%** |

**Key Observations:**

1. **Version-Specific Behavior:** MariaDB 12.2.2 baseline handles 128 threads significantly better than 11.8.6 (6,080 vs 3,635 TPS) due to improved concurrent I/O handling. At this concurrency, 12.2.2 doesn't need thread pool — it already maintains high CPU utilization (43%) and disk bandwidth (1.77 GB/s).

2. **Thread Pool Value Shifts to Extreme Oversubscription:** Thread pool provides minimal benefit until 256+ threads, where both versions see ~80% throughput gains at 512 threads.

3. **Recommendation:** For mixed I/O workloads, **upgrade to MariaDB 12.2.2 first** (67% better than 11.8.6 at 128 threads). Only enable thread pool if you regularly operate at 256+ concurrent connections.

### 9.4. 32GB Buffer Pool Results

#### 9.4.1. Performance Table

![TPS Table - 32GB Buffer Pool](graphs_out/table_tps_32g.png)

#### 9.4.2. Throughput Graph

![TPS Graph - 32GB Buffer Pool](graphs_out/throughput_tps_32g.png)

#### 9.4.3. Thread Pool Analysis (32GB - Memory Bound)

*Note: This is a secondary experiment. With memory-resident workloads, storage speed is not a bottleneck.*

**Thread Pool Effect Summary:**

| Concurrency | Baseline (11.8.6) | Thread Pool | Delta |
|-------------|-------------------|-------------|-------|
| 1-16 threads | 517 TPS | 412 TPS | -20% |
| 64 threads | 8,298 TPS | 7,869 TPS | -5% |
| 128 threads | **10,694 TPS** | 10,232 TPS | -4% |
| 512 threads | 3,921 TPS | 3,318 TPS | -15% |

**Key Observation:**

When the entire working set fits in memory, **thread pool provides no benefit**. The baseline configuration achieves peak performance (~10,700 TPS) at 128 threads without thread pool. Both configurations degrade beyond 128 threads due to lock contention, which thread pool cannot solve.

**Recommendation:** For memory-resident OLTP workloads, skip thread pool entirely. Focus on lock optimization and query tuning instead.

## 10. Limitations and Considerations

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

## 11. Reproducibility

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
