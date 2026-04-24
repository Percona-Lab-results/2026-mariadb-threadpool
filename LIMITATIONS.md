# Limitations and Considerations

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
