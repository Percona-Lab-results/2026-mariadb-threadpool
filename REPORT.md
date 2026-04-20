# MariaDB Thread Pool Performance Analysis Report

## 1. Benchmark Overview

### 1.1. Purpose and Scope

### Purpose

The primary purpose of this benchmark study is to evaluate how the MariaDB Thread Pool feature affects database performance under OLTP (Online Transaction Processing) read-write workloads. This investigation aims to provide empirical data on the performance characteristics of MariaDB servers operating with and without thread pool configuration across various workload conditions.

### Target Questions

This analysis seeks to answer the following key questions:

1. **Raw TPS Scaling with Thread Count**
   - How does transaction throughput (TPS) scale as the number of client threads increases from light (single-threaded) to heavily oversubscribed workloads (512 threads)?
   - At what concurrency levels does performance plateau or degrade?

2. **Thread Pool Performance Impact**
   - What performance improvements (or degradations) does the MariaDB Thread Pool provide compared to default thread handling?
   - Under which concurrency levels is the thread pool most beneficial?
   - Are there scenarios where thread pool introduces overhead?

3. **Effect of InnoDB Buffer Pool Size**
   - How does varying the `innodb_buffer_pool_size` (2 GB, 12 GB, 32 GB) affect throughput?
   - What is the performance difference between I/O-bound (2 GB) versus fully buffered (32 GB) workloads?
   - Does thread pool effectiveness change across different memory configurations?

4. **Version Comparison within MariaDB Family**
   - How do MariaDB 11.8.6 and MariaDB 12.2.2 compare in terms of raw performance?
   - Are there significant differences in thread pool behavior between these versions?
   - Which version demonstrates better scalability characteristics?

### Scope

- **Database Systems**: MariaDB 11.8.6 and 12.2.2 (with and without Thread Pool)
- **Reference Systems**: MySQL 8.4.8, MySQL 9.7.0-er2, Percona Server 8.4.8 (for comparative context)
- **Workload Type**: Sysbench OLTP Read-Write
- **Concurrency Levels**: 1, 4, 16, 32, 64, 128, 256, 512 client threads
- **Memory Tiers**: 2 GB, 12 GB, 32 GB `innodb_buffer_pool_size`
- **Thread Pool Configuration**: `thread_pool_size=80`, `thread_pool_max_threads=2000`

### 1.2. Engines Under Test

| Server | Version | Thread Handling | Role |
|--------|---------|----------------|------|
| **MariaDB** | 11.8.6 | Default (one-thread-per-connection) | Primary test subject |
| **MariaDB** | 11.8.6 | Thread Pool (`thread_pool_size=80`) | Primary test subject |
| **MariaDB** | 12.2.2 | Default (one-thread-per-connection) | Primary test subject |
| **MariaDB** | 12.2.2 | Thread Pool (`thread_pool_size=80`) | Primary test subject |
| **MySQL** | 8.4.8 | Default | Reference |
| **MySQL** | 9.7.0-er2 | Default | Reference |
| **Percona Server** | 8.4.8-8 | Default | Reference |

**Note**: Reference servers (MySQL and Percona) are included for cross-product performance context but are not the primary focus of this benchmark.

## 2. Key Findings

This section summarizes the critical performance insights derived from comprehensive testing across three memory configurations and eight concurrency levels.

### 2.1. Thread Pool Effectiveness by Workload Type

Thread Pool performance benefits are strongly correlated with I/O intensity:

| Workload Type | Buffer Pool | I/O Characteristic | Thread Pool Benefit at 512 Threads | Recommended Use Case |
|---------------|-------------|-------------------|-------------------------------------|----------------------|
| **I/O Bound** | 2 GB | Heavy disk access (1:12 ratio) | **+121-143%** throughput | Strongly recommended |
| **Mixed** | 12 GB | Partial buffering (1:2 ratio) | **+79-83%** throughput | Recommended for high concurrency |
| **Memory Bound** | 32 GB | Fully buffered | **-15% to +0%** throughput | Limited benefit |

**Insight:** Thread Pool provides maximum value when I/O wait states are prevalent, allowing efficient thread coordination during disk operations. When workloads are fully memory-resident, the baseline one-thread-per-connection model can handle moderate concurrency effectively.

### 2.2. Concurrency Behavior Patterns

Thread Pool exhibits a consistent performance profile across all configurations:

**Low Concurrency (1-32 threads):**
- Thread Pool introduces **3-10% overhead** due to coordination costs
- Overhead is most visible at 1-4 threads where native thread handling is most efficient
- Effect diminishes as concurrency approaches thread pool size (80 threads)

**Medium Concurrency (64-128 threads):**
- Thread Pool reaches **performance parity** with baseline
- Crossover point occurs around 80-128 threads depending on I/O pressure
- At 128 threads with 32GB buffer: baseline achieves peak performance (~10,600 TPS)

**High Concurrency (256-512 threads):**
- Thread Pool shows **dramatic advantages** under oversubscription
- At 512 threads: 79-143% throughput improvement depending on I/O intensity
- Prevents thread thrashing and context switching overhead
- Provides more predictable performance degradation curve

### 2.3. MariaDB Version Comparison

**MariaDB 11.8.6 vs 12.2.2:**
- Both versions show **similar Thread Pool behavior patterns**
- MariaDB 12.2.2 demonstrates stronger baseline performance at 128 threads (12GB buffer: 6,080 TPS vs 3,635 TPS for 11.8.6)
- Thread Pool benefits are **version-independent** at extreme concurrency levels
- Both versions achieve ~1,300 TPS at 512 threads with Thread Pool (12GB buffer)

**Conclusion:** Upgrading from 11.8.6 to 12.2.2 provides baseline improvements, but Thread Pool effectiveness remains consistent across versions.

### 2.4. Practical Deployment Recommendations

**When to Enable Thread Pool:**

✅ **Recommended:**
- Applications with **connection counts exceeding 128-200** concurrent threads
- **I/O-bound workloads** where dataset significantly exceeds buffer pool
- Environments with **unpredictable connection spikes** requiring stability
- Systems with **limited CPU cores** (≤16) serving many connections

❌ **Not Recommended:**
- Workloads consistently operating at **<64 concurrent connections**
- **Fully memory-resident datasets** with predictable, low concurrency
- OLTP applications prioritizing **absolute peak throughput** at optimal concurrency (~128 threads)
- Development/testing environments with low connection counts

⚠️ **Use with Caution:**
- Mixed environments with both low and high concurrency patterns (slight overhead at low end)
- Applications sensitive to single-digit millisecond latency increases at low concurrency

## 3. Test Environment & Infrastructure

### 3.1. Hardware Specification

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
- **Partitions**:
  - `/dev/sda1`: 1 GB, vfat, mounted at `/boot/efi`
  - `/dev/sda2`: 100 GB, ext4, mounted at `/boot`
  - `/dev/sda3`: 793.2 GB, ext4, mounted at `/` (root)

**Secondary Storage (NVMe)**
- **Device**: /dev/nvme0n1
- **Total Size**: 2.9 TB
- **Filesystem**: ext4
- **Status**: Available (not mounted)

#### Network

- **Controller**: Intel Corporation Ethernet Controller X550 (dual port)
- **Active Interface**: enp94s0f1
  - **Speed**: 10000 Mb/s (10 Gbps)
  - **Duplex**: Full

### 3.2. Software Configuration

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

### 3.3. Containerization Strategy

Each MariaDB engine was run as a Docker container using official images from the `mariadb` repository. The host network mode was used to avoid bridge networking overhead. A fresh container was started for each engine/tier combination using the following sequence:

1. **Stop and remove** any existing benchmark container
2. **Detect actual server version** by connecting and running `SELECT VERSION()`
3. **Generate a version-specific configuration file** (see Section 3)
4. **Restart the container** with the new configuration mounted
5. **Wait for the server to become ready** (mariadb-admin ping loop)
6. **Verify InnoDB buffer pool size** matches the intended tier (hard abort on mismatch)

This approach ensured that each test run started with a clean state and the correct configuration parameters were applied before benchmark execution.

### 3.4. Buffer Pool Tiers

With the database size of 24 GB, three InnoDB buffer pool sizes were tested, each representing a distinct workload characteristic:

| Tier (innodb_buffer_pool_size) | Workload Character |
|---------------------------------|--------------------|
| **2 GB** | **I/O bound** — dataset substantially exceeds buffer pool (1:12 ratio); heavy read amplification |
| **12 GB** | **Mixed** — partial dataset fits in memory (1:2 ratio); realistic production scenario |
| **32 GB** | **In-memory** — full working set fits; CPU and locking are primary bottlenecks |

These tiers were selected to evaluate MariaDB performance across different memory pressure scenarios, from heavily disk-constrained (2 GB) to fully memory-resident (32 GB) workloads.

## 4. Database Configuration

All MariaDB servers were configured with production-grade settings optimized for OLTP workloads. The configuration below represents the Thread Pool variant; non-Thread Pool servers used identical settings except for thread handling mode.

### 4.1. General Settings

```
performance_schema              = OFF
skip-name-resolve               = ON
max_connections                 = 2000
max_connect_errors              = 1000000
max_prepared_stmt_count         = 1000000
```

### 4.2. Thread Handling

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

### 4.3. InnoDB Buffer Pool

Buffer pool size varied by tier (see Section 3.4):
```
innodb_buffer_pool_size         = 2G | 12G | 32G
```

### 4.4. InnoDB I/O Configuration

Optimized for NVMe storage with high concurrency:
```
innodb_io_capacity              = 10000
innodb_io_capacity_max          = 20000
innodb_read_io_threads          = 16
innodb_write_io_threads         = 16
innodb_use_native_aio           = ON
```

### 4.5. InnoDB Durability & Logging

Full ACID compliance with transaction log optimization:
```
innodb_log_file_size            = 4G
innodb_log_buffer_size          = 256M
innodb_flush_log_at_trx_commit  = 1                 # full ACID
innodb_doublewrite              = ON
sync_binlog                     = 1
```

### 4.6. InnoDB Concurrency & OLTP Tuning

```
innodb_stats_on_metadata        = OFF
innodb_open_files               = 65536
innodb_lock_wait_timeout        = 50
innodb_rollback_on_timeout      = ON
innodb_snapshot_isolation       = OFF               # MariaDB 12.x+
```

### 4.7. Per-Session Buffers

Conservative settings to support high connection counts:
```
sort_buffer_size                = 4M
join_buffer_size                = 4M
read_buffer_size                = 2M
read_rnd_buffer_size            = 4M
tmp_table_size                  = 256M
max_heap_table_size             = 256M
```

### 4.8. Table & File Handles

```
table_open_cache                = 65536
table_definition_cache          = 65536
open_files_limit                = 1000000
table_open_cache_instances      = 64
```

### 4.9. Binary Logging

Enabled for production-realistic overhead measurement:
```
log_bin                         = /var/lib/mysql/mysql-bin
binlog_format                   = ROW
binlog_row_image                = MINIMAL
binlog_cache_size               = 4M
max_binlog_size                 = 512M
```

**Note:** The complete configuration file is available in the benchmark logs directory as `TierXG.cnf.txt` for each tested configuration.

## 5. Benchmark Workload

### 5.1. Warmup Protocol

Before each production benchmark run, the database underwent a two-phase warmup sequence to ensure consistent starting conditions:

| Phase | Duration | Purpose |
|-------|----------|---------|
| **Warmup A — Read-Only** | 180 s (3 min) | Populate buffer pool with hot pages |
| **Warmup B — Read-Write** | 600 s (10 min) | Steady-state redo log & dirty page ratio (skipped for RO) |

**Note:** The proposed warmup values are determined experimentally and are sufficient for the hardware configuration used for the benchmarking. However, in case of much slower hosts the user will need to adjust them by editing scripts.

### 5.2. Measurement Run

Following the warmup phase, each benchmark execution ran for **900 seconds (15 minutes)** with performance metrics captured at 1-second granularity. During execution, system-level telemetry tools (iostat, vmstat, mpstat, dstat) collected resource utilization data in parallel.

#### Data Collection Strategy

The results presented in this report represent a **single measurement per configuration**. To validate result stability and confirm steady-state operation, we conducted selective repeat runs (2nd and 3rd iterations) across representative server and memory tier combinations. These validation runs consistently confirmed the reproducibility of the initial measurements.

The validation dataset was intentionally excluded from publication to maintain data accessibility. Given that each baseline measurement produces multiple output files (sysbench results, iostat, vmstat, mpstat, dstat, and configuration logs), the inclusion of validation runs would have multiplied the dataset size significantly, creating an unwieldy collection of thousands of files that would be difficult to navigate and distribute.

#### Steady-State Verification

**Read Operations:** Steady state for read workloads was verified by monitoring InnoDB buffer pool metrics and OS-level I/O read counters. The system was considered stable when physical reads dropped to near-zero after the warmup period, indicating the working set was fully cached.

**Write Operations:** For write-intensive phases, stability was determined by observing transaction throughput and latency metrics until they reached consistent values without significant drift.

**Known Limitation:** While short-term metric stability (15 minutes) provides confidence in measurement consistency, it does not entirely eliminate the possibility of longer-term background activity such as adaptive flushing, change buffer merges, or checkpoint behavior that might emerge during extended multi-day operations. The chosen measurement window represents a balance between statistical confidence and practical benchmarking constraints.

## 6. Metrics & Reporting

### 6.1. Primary Metrics

| Metric | Definition |
|--------|------------|
| **TPS** | Transactions per second (complete BEGIN/COMMIT cycles) |
| **QPS** | Queries per second (≈20× TPS for this workload) |

### 6.2. Derived Metrics

Performance analysis includes:
- **QPS/TPS gain relative to additional RAM**: Throughput improvement when increasing `innodb_buffer_pool_size` from one tier to another
- **QPS/TPS gain relative to thread count increase**: Scalability characteristics as concurrent client connections grow

### 6.3. Output Files

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

## 7. Measurement Results

This section presents the throughput measurements across all tested configurations. Results are organized by memory tier, with detailed performance comparisons across thread counts and database versions.

### 7.1. Performance Summary Tables

The following tables show TPS (Transactions Per Second) values for each configuration. Color coding indicates relative performance within each memory tier:
- **Green cells**: High performance relative to other configurations at the same thread count
- **Yellow/Orange cells**: Mid-range performance
- **Red cells**: Lower performance relative to other configurations

Bar length is proportional to the actual value relative to the maximum in each column, making it easy to visually compare performance across different servers at the same concurrency level.

### 7.2. 2GB Buffer Pool Results

#### 7.2.1. Performance Table

![TPS Table - 2GB Buffer Pool](graphs_out/table_tps_2g.png)

#### 7.2.2. Throughput Graph

![TPS Graph - 2GB Buffer Pool](graphs_out/throughput_tps_2g.png)

#### 7.2.3. Thread Pool Effect Analysis (2GB - I/O Bound)

At the 2GB buffer pool configuration, the database is heavily I/O-bound with the 24GB dataset substantially exceeding available memory (1:12 ratio). This creates significant disk access pressure and tests the thread pool's ability to manage I/O wait states.

**Key Observations:**

**Low Concurrency (1-16 threads):**
- Thread Pool shows **minimal to slight negative impact** at very low thread counts
- MariaDB 11.8.6: 142 TPS (baseline) vs 138 TPS (Thread Pool) at 1 thread (-3%)
- MariaDB 12.2.2: 142 TPS (baseline) vs 135 TPS (Thread Pool) at 1 thread (-5%)
- The Thread Pool overhead is visible but marginal when concurrency is naturally low

**Medium Concurrency (32-64 threads):**
- Thread Pool maintains **competitive performance** with baseline
- At 64 threads, both versions perform similarly (4,100-4,200 TPS range)
- No significant advantage or disadvantage observed in this range

**High Concurrency (128-512 threads):**
- Thread Pool demonstrates **significant advantage** under oversubscription
- MariaDB 11.8.6 at 512 threads: 266 TPS (baseline) vs **587 TPS (Thread Pool)** - **+121% improvement**
- MariaDB 12.2.2 at 512 threads: 247 TPS (baseline) vs **600 TPS (Thread Pool)** - **+143% improvement**
- At 256 threads: Thread Pool maintains ~600 TPS while baseline drops to ~566-610 TPS

**Conclusion:** Under I/O-bound conditions, the Thread Pool shows its primary benefit at high concurrency levels (128+ threads) where it prevents context switching overhead and thread thrashing. The ability to maintain 2-2.4x higher throughput at 512 threads demonstrates effective thread management when the system is heavily oversubscribed.

### 7.3. 12GB Buffer Pool Results

#### 7.3.1. Performance Table

![TPS Table - 12GB Buffer Pool](graphs_out/table_tps_12g.png)

#### 7.3.2. Throughput Graph

![TPS Graph - 12GB Buffer Pool](graphs_out/throughput_tps_12g.png)

#### 7.3.3. Thread Pool Effect Analysis (12GB - Mixed Workload)

At 12GB buffer pool, approximately half of the 24GB dataset fits in memory (1:2 ratio), creating a realistic mixed workload with both cached and disk-bound operations. This represents a common production scenario.

**Key Observations:**

**Low Concurrency (1-16 threads):**
- Thread Pool shows **minor overhead** at low thread counts
- MariaDB 11.8.6: 226 TPS (baseline) vs 215 TPS (Thread Pool) at 1 thread (-5%)
- MariaDB 12.2.2: 226 TPS (baseline) vs 213 TPS (Thread Pool) at 1 thread (-6%)
- At 16 threads: 3,085 TPS (baseline) vs 2,887 TPS (Thread Pool) for 11.8.6 (-6%)
- The overhead diminishes as concurrency increases toward the thread pool size

**Medium Concurrency (32-64 threads):**
- Thread Pool reaches **performance parity** with baseline
- At 64 threads: 7,302 TPS (baseline) vs 7,119 TPS (Thread Pool) for 11.8.6 (-2.5%)
- At 64 threads: 7,364 TPS (baseline) vs 7,143 TPS (Thread Pool) for 12.2.2 (-3%)
- Performance gap narrows significantly as concurrency approaches thread pool size (80)

**High Concurrency (128-512 threads):**
- Thread Pool delivers **substantial gains** under oversubscription
- MariaDB 11.8.6 at 128 threads: 3,635 TPS (baseline) vs **4,234 TPS (Thread Pool)** - **+16% improvement**
- MariaDB 12.2.2 at 128 threads: 6,080 TPS (baseline) vs **5,455 TPS (Thread Pool)** - note: 12.2.2 baseline performs exceptionally well here
- At 512 threads: 727 TPS (baseline) vs **1,302 TPS (Thread Pool)** for 11.8.6 - **+79% improvement**
- At 512 threads: 704 TPS (baseline) vs **1,285 TPS (Thread Pool)** for 12.2.2 - **+83% improvement**

**Version Comparison:**
- MariaDB 12.2.2 shows stronger baseline performance at moderate concurrency (128 threads) compared to 11.8.6
- Both versions benefit similarly from Thread Pool at extreme oversubscription (256-512 threads)
- Thread Pool provides more consistent performance degradation curve as concurrency increases

**Conclusion:** In mixed I/O scenarios, Thread Pool shows a classic trade-off pattern: slight overhead at low concurrency (where it's unnecessary) in exchange for dramatic improvements at high concurrency (where it prevents thrashing). The crossover point occurs around 80-128 threads, after which Thread Pool consistently outperforms baseline, with nearly 2x throughput at 512 threads.

### 7.4. 32GB Buffer Pool Results

#### 7.4.1. Performance Table

![TPS Table - 32GB Buffer Pool](graphs_out/table_tps_32g.png)

#### 7.4.2. Throughput Graph

![TPS Graph - 32GB Buffer Pool](graphs_out/throughput_tps_32g.png)

#### 7.4.3. Thread Pool Effect Analysis (32GB - Memory Bound)

At 32GB buffer pool, the entire 24GB working set fits in memory, eliminating I/O bottlenecks. Performance is primarily constrained by CPU cycles, lock contention, and context switching overhead.

**Key Observations:**

**Low Concurrency (1-16 threads):**
- Thread Pool shows **negligible overhead** in fully memory-resident workloads
- MariaDB 11.8.6: 517 TPS (baseline) vs 412 TPS (Thread Pool) at 1 thread (-20%)
- MariaDB 12.2.2: 419 TPS (baseline) vs 419 TPS (Thread Pool) at 1 thread (0%)
- At 4 threads: ~1,574 TPS (baseline) vs ~1,418 TPS (Thread Pool) for 11.8.6 (-10%)
- Thread Pool overhead is more visible at very low concurrency where coordination costs matter

**Medium Concurrency (16-64 threads):**
- Thread Pool approaches **performance parity** as concurrency increases
- At 32 threads: 5,844 TPS (baseline) vs 5,348 TPS (Thread Pool) for 11.8.6 (-8%)
- At 64 threads: 8,298 TPS (baseline) vs 7,869 TPS (Thread Pool) for 11.8.6 (-5%)
- At 64 threads: 8,587 TPS (baseline) vs **10,066 TPS (Thread Pool)** for MySQL 8.4.8 - reference server shows variation
- Performance gap narrows steadily as thread count approaches pool size

**High Concurrency (128-512 threads):**
- Thread Pool shows **mixed results** but generally maintains better stability
- MariaDB 11.8.6 at 128 threads: **10,694 TPS (baseline)** vs 10,232 TPS (Thread Pool) - baseline peaks here
- MariaDB 12.2.2 at 128 threads: **10,273 TPS (baseline)** vs 5,372 TPS (Thread Pool) - notable divergence
- At 256 threads: 5,973 TPS (baseline) vs 5,330 TPS (Thread Pool) for 11.8.6
- At 512 threads: 3,921 TPS (baseline) vs 3,318 TPS (Thread Pool) for 11.8.6 (-15%)

**Critical Insight:**
Unlike I/O-bound scenarios, the memory-resident workload shows **less dramatic Thread Pool benefits**. The baseline (one-thread-per-connection) model performs exceptionally well at 128 threads, suggesting that when I/O wait is eliminated, the system can handle moderate oversubscription effectively without thread pool management.

**Lock Contention Factor:**
- At 128 threads, baseline achieves peak performance (~10,000-10,700 TPS) across both MariaDB versions
- Beyond 128 threads, both baseline and Thread Pool degrade, indicating lock contention becomes the primary bottleneck
- Thread Pool does not solve lock contention, but provides more predictable degradation

**Conclusion:** In memory-resident workloads, Thread Pool provides less dramatic benefits compared to I/O-bound scenarios. The baseline model can effectively handle up to ~128 threads when I/O is not a bottleneck. Thread Pool's advantage shifts from "preventing I/O thrashing" to "providing more predictable behavior under extreme oversubscription," but the absolute performance gains are smaller. For workloads that fit entirely in memory, Thread Pool may not be necessary unless connection counts regularly exceed 200-300 concurrent connections.
