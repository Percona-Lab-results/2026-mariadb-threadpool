# Reproducibility

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
