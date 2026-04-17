# Hardware Specification

## System Information

- **Platform**: Linux
- **Release**: Ubuntu 24.04 LTS (noble)
- **Kernel**: 6.8.0-60-generic
- **Architecture**: CPU = 64-bit, OS = 64-bit
- **Virtualized**: No virtualization detected

## CPU

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

## NUMA

- **NUMA Nodes**: 2
- **Node 0**: 95288 MB (CPUs: 0-19, 40-59)
- **Node 1**: 96748 MB (CPUs: 20-39, 60-79)

## Memory

- **Total Memory**: 187.5G
- **Swap Size**: 8.0G

## Storage Configuration

### Primary Storage (SDA - System Disk)
- **Device**: /dev/sda
- **Total Size**: 894.3 GB
- **Partitions**:
  - `/dev/sda1`: 1 GB, vfat, mounted at `/boot/efi`
  - `/dev/sda2`: 100 GB, ext4, mounted at `/boot`
  - `/dev/sda3`: 793.2 GB, ext4, mounted at `/` (root)

### Secondary Storage (NVMe)
- **Device**: /dev/nvme0n1
- **Total Size**: 2.9 TB
- **Filesystem**: ext4
- **Status**: Available (not mounted)

## Network

- **Controller**: Intel Corporation Ethernet Controller X550 (dual port)
- **Active Interface**: enp94s0f1
  - **Speed**: 10000 Mb/s (10 Gbps)
  - **Duplex**: Full
