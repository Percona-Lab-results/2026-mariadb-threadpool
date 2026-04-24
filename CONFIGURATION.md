# Database Configuration

All database servers were configured with production-grade settings optimized for OLTP workloads. InnoDB I/O parameters were tuned for NVMe storage to utilize its low latency and high throughput capabilities.

## General Settings

```
performance_schema              = OFF
skip-name-resolve               = ON
max_connections                 = 2000
max_connect_errors              = 1000000
max_prepared_stmt_count         = 1000000
```

## Thread Handling

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

## InnoDB Buffer Pool

Buffer pool size varied by tier (see Section 3.4):
```
innodb_buffer_pool_size         = 2G | 12G | 32G
```

## InnoDB I/O Configuration

Optimized for NVMe storage with high concurrency:
```
innodb_io_capacity              = 10000
innodb_io_capacity_max          = 20000
innodb_read_io_threads          = 16
innodb_write_io_threads         = 16
innodb_use_native_aio           = ON
```

## InnoDB Durability & Logging

Full ACID compliance with transaction log optimization:
```
innodb_log_file_size            = 4G
innodb_log_buffer_size          = 256M
innodb_flush_log_at_trx_commit  = 1                 # full ACID
innodb_doublewrite              = ON
sync_binlog                     = 1
```

## InnoDB Concurrency & OLTP Tuning

```
innodb_stats_on_metadata        = OFF
innodb_open_files               = 65536
innodb_lock_wait_timeout        = 50
innodb_rollback_on_timeout      = ON
innodb_snapshot_isolation       = OFF               # MariaDB 12.x+
```

## Per-Session Buffers

Conservative settings to support high connection counts:
```
sort_buffer_size                = 4M
join_buffer_size                = 4M
read_buffer_size                = 2M
read_rnd_buffer_size            = 4M
tmp_table_size                  = 256M
max_heap_table_size             = 256M
```

## Table & File Handles

```
table_open_cache                = 65536
table_definition_cache          = 65536
open_files_limit                = 1000000
table_open_cache_instances      = 64
```

## Binary Logging

Enabled for production-realistic overhead measurement:
```
log_bin                         = /var/lib/mysql/mysql-bin
binlog_format                   = ROW
binlog_row_image                = MINIMAL
binlog_cache_size               = 4M
max_binlog_size                 = 512M
```

**Note:** The complete configuration file is available in the benchmark logs directory as `TierXG.cnf.txt` for each tested configuration.
