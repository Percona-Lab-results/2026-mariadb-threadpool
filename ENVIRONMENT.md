# Test Environment & Infrastructure

## Hardware Specification

### System Information

- **Platform**: Linux
- **Release**: Ubuntu 24.04 LTS (noble)
- **Kernel**: 6.8.0-60-generic
- **Architecture**: CPU = 64-bit, OS = 64-bit
- **Virtualized**: No virtualization detected

### CPU

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

### NUMA

- **NUMA Nodes**: 2
- **Node 0**: 95288 MB (CPUs: 0-19, 40-59)
- **Node 1**: 96748 MB (CPUs: 20-39, 60-79)

### Memory

- **Total Memory**: 187.5G
- **Swap Size**: 8.0G

### Storage Configuration

**Primary Storage (SDA - System Disk)**
- **Device**: /dev/sda
- **Total Size**: 894.3 GB
- **Filesystem**: ext4

**Secondary Storage (NVMe)**
- **Device**: /dev/nvme0n1
- **Total Size**: 2.9 TB
- **Filesystem**: ext4

## Software Configuration

### Operating System

- **Distribution**: Ubuntu 24.04 LTS (noble)
- **Kernel**: 6.8.0-60-generic
- **Architecture**: 64-bit

### Containerization

- **Docker**: Used for database server deployment
- **Network Mode**: `--network host` (native host networking, no NAT overhead)

### Benchmark Tool

- **Sysbench**: Version 1.0.20
- **LuaJIT**: 2.1.0-beta3 (system)
- **Test Script**: OLTP Read-Write (built-in)

### Telemetry Tools

System performance metrics were collected continuously during each benchmark run:

- **iostat**: I/O statistics monitoring
- **vmstat**: Virtual memory and system statistics
- **mpstat**: Multi-processor statistics
- **dstat**: Combined system resource statistics
- **Sampling Interval**: 1 second for all tools
- **Collection Period**: Full duration of each 15-minute test run

## Containerization Strategy

Each MariaDB engine was run as a Docker container using official images from the `mariadb` repository. The host network mode was used to avoid bridge networking overhead. A fresh container was started for each engine/tier combination using the following sequence:

1. **Stop and remove** any existing benchmark container
2. **Detect actual server version** by connecting and running `SELECT VERSION()`
3. **Generate a version-specific configuration file** (see Section 3)
4. **Restart the container** with the new configuration mounted
5. **Wait for the server to become ready** (mariadb-admin ping loop)
6. **Verify InnoDB buffer pool size** matches the intended tier (hard abort on mismatch)

This approach ensured that each test run started with a clean state and the correct configuration parameters were applied before benchmark execution.

## Buffer Pool Tiers

With the database size of 24 GB, three InnoDB buffer pool sizes were tested, each representing a distinct workload characteristic:

| Tier (innodb_buffer_pool_size) | Workload Character |
|---------------------------------|--------------------|
| **2 GB** | **I/O bound** — dataset substantially exceeds buffer pool (1:12 ratio); heavy read amplification |
| **12 GB** | **Mixed** — partial dataset fits in memory (1:2 ratio); realistic production scenario |
| **32 GB** | **In-memory** — full working set fits; CPU and locking are primary bottlenecks |

These tiers were selected to evaluate MariaDB performance across different memory pressure scenarios, from heavily disk-constrained (2 GB) to fully memory-resident (32 GB) workloads.
