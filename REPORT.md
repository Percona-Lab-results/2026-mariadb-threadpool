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
