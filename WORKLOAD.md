# Benchmark Workload

## Warmup Protocol

Before each production benchmark run, the database underwent a two-phase warmup sequence to ensure consistent starting conditions:

| Phase | Duration | Purpose |
|-------|----------|---------|
| **Warmup A — Read-Only** | 180 s (3 min) | Populate buffer pool with hot pages |
| **Warmup B — Read-Write** | 600 s (10 min) | Steady-state redo log & dirty page ratio (skipped for RO) |

**Note:** The proposed warmup values are determined experimentally and are sufficient for the hardware configuration used for the benchmarking. However, in case of much slower hosts the user will need to adjust them by editing scripts.

## Measurement Run

Following the warmup phase, each benchmark execution ran for **900 seconds (15 minutes)** with performance metrics captured at 1-second granularity. During execution, system-level telemetry tools (iostat, vmstat, mpstat, dstat) collected resource utilization data in parallel.

### Data Collection Strategy

The results presented in this report represent a **single measurement per configuration**. To validate result stability and confirm steady-state operation, we conducted selective repeat runs (2nd and 3rd iterations) across representative server and memory tier combinations. These validation runs consistently confirmed the reproducibility of the initial measurements.

The validation dataset was intentionally excluded from publication to maintain data accessibility. Given that each baseline measurement produces multiple output files (sysbench results, iostat, vmstat, mpstat, dstat, and configuration logs), the inclusion of validation runs would have multiplied the dataset size significantly, creating an unwieldy collection of thousands of files that would be difficult to navigate and distribute.

### Steady-State Verification

**Read Operations:** Steady state for read workloads was verified by monitoring InnoDB buffer pool metrics and OS-level I/O read counters. The system was considered stable when physical reads dropped to near-zero after the warmup period, indicating the working set was fully cached.

**Write Operations:** For write-intensive phases, stability was determined by observing transaction throughput and latency metrics until they reached consistent values without significant drift.

**Known Limitation:** While short-term metric stability (15 minutes) provides confidence in measurement consistency, it does not entirely eliminate the possibility of longer-term background activity such as adaptive flushing, change buffer merges, or checkpoint behavior that might emerge during extended multi-day operations. The chosen measurement window represents a balance between statistical confidence and practical benchmarking constraints.
