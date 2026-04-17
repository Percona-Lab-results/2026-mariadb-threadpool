#!/usr/bin/env python3
"""
Generate throughput graphs from sysbench benchmark results.
Creates separate graphs for each memory tier (2GB, 12GB, 32GB).
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
from matplotlib.ticker import FuncFormatter

# Configuration
BENCHMARK_DIR = Path(__file__).parent / "benchmark_logs"
OUTPUT_DIR = Path(__file__).parent / "graphs_out"
MEMORY_TIERS = ['2G', '12G', '32G']
THREAD_COUNTS = [1, 4, 16, 32, 64, 128, 256, 512]

# Server configurations
SERVER_MAPPING = {
    'mariadb/11.8.6-MariaDB-ubu2404': 'MariaDB 11.8.6',
    'mariadb/12.2.2-MariaDB-ubu2404': 'MariaDB 12.2.2',
    'mariadb-thp/11.8.6-MariaDB-ubu2404': 'MariaDB 11.8.6 (Thread Pool)',
    'mariadb-thp/12.2.2-MariaDB-ubu2404': 'MariaDB 12.2.2 (Thread Pool)',
    'mysql/8.4.8': 'MySQL 8.4.8',
    'mysql/9.7.0-er2': 'MySQL 9.7.0-er2',
    'percona/8.4.8-8': 'Percona Server 8.4.8',
}

# Color scheme for different servers (vibrant colors like reference)
COLORS = {
    'MariaDB 11.8.6': '#4CAF50',        # Neutral green
    'MariaDB 12.2.2': '#E63946',        # Red
    'MariaDB 11.8.6 (Thread Pool)': '#00BCD4',  # Cyan
    'MariaDB 12.2.2 (Thread Pool)': '#FFB703',  # Yellow/Gold
    'MySQL 8.4.8': '#457B9D',           # Blue
    'MySQL 9.7.0-er2': '#6A4C93',       # Purple
    'Percona Server 8.4.8': '#118AB2',  # Cyan-blue
}

# Line styles - all solid lines like reference
LINE_STYLES = {
    'MariaDB 11.8.6': '-',
    'MariaDB 12.2.2': '-',
    'MariaDB 11.8.6 (Thread Pool)': '-',
    'MariaDB 12.2.2 (Thread Pool)': '-',
    'MySQL 8.4.8': '-',
    'MySQL 9.7.0-er2': '-',
    'Percona Server 8.4.8': '-',
}

MARKER_STYLES = {
    'MariaDB 11.8.6': 'o',           # Circle
    'MariaDB 12.2.2': 'o',           # Circle
    'MariaDB 11.8.6 (Thread Pool)': 's',  # Square
    'MariaDB 12.2.2 (Thread Pool)': 'D',  # Diamond
    'MySQL 8.4.8': 's',              # Square
    'MySQL 9.7.0-er2': '^',          # Triangle up
    'Percona Server 8.4.8': 'v',     # Triangle down
}

# Whether markers should be filled (True) or outlined (False)
MARKER_FILLED = {
    'MariaDB 11.8.6': True,          # Solid - Orange circle
    'MariaDB 12.2.2': False,         # Outlined - Red circle
    'MariaDB 11.8.6 (Thread Pool)': True,   # Solid - Green square
    'MariaDB 12.2.2 (Thread Pool)': False,  # Outlined - Yellow diamond
    'MySQL 8.4.8': False,            # Outlined - Blue square
    'MySQL 9.7.0-er2': True,         # Solid - Purple triangle
    'Percona Server 8.4.8': False,   # Outlined - Cyan triangle
}


def parse_sysbench_file(filepath):
    """Extract TPS and QPS from sysbench output file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        # Look for the summary section
        # transactions:                        842222 (935.79 per sec.)
        tps_match = re.search(r'transactions:\s+\d+\s+\((\d+\.?\d*)\s+per sec\.\)', content)
        # queries:                             16844440 (18715.81 per sec.)
        qps_match = re.search(r'queries:\s+\d+\s+\((\d+\.?\d*)\s+per sec\.\)', content)

        if tps_match and qps_match:
            tps = float(tps_match.group(1))
            qps = float(qps_match.group(1))
            return tps, qps
        else:
            print(f"Warning: Could not parse {filepath}")
            return None, None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None, None


def collect_data():
    """Collect all benchmark data organized by memory tier and server."""
    data = defaultdict(lambda: defaultdict(lambda: {'threads': [], 'tps': [], 'qps': []}))

    for server_path, server_name in SERVER_MAPPING.items():
        server_dir = BENCHMARK_DIR / server_path
        if not server_dir.exists():
            print(f"Warning: {server_dir} does not exist, skipping")
            continue

        for mem_tier in MEMORY_TIERS:
            for threads in THREAD_COUNTS:
                filename = f"Tier{mem_tier}_RW_{threads}th.sysbench.txt"
                filepath = server_dir / filename

                if filepath.exists():
                    tps, qps = parse_sysbench_file(filepath)
                    if tps is not None and qps is not None:
                        data[mem_tier][server_name]['threads'].append(threads)
                        data[mem_tier][server_name]['tps'].append(tps)
                        data[mem_tier][server_name]['qps'].append(qps)

    return data


def thousands_formatter(x, pos):
    """Format y-axis values in thousands with 'k' suffix."""
    if x >= 1000:
        return f'{int(x/1000)}k'
    return f'{int(x)}'


def create_graph(mem_tier, data, metric='tps'):
    """Create a single graph for a memory tier."""
    # Create figure with white background
    # Target 1600px width at 100 DPI = 16 inches
    fig, ax = plt.subplots(figsize=(16, 9), facecolor='white', dpi=100)
    ax.set_facecolor('white')

    metric_label = 'Transactions per Second (TPS)' if metric == 'tps' else 'Queries per Second (QPS)'

    # Sort servers to plot MariaDB servers first
    servers = sorted(data.keys(),
                    key=lambda x: (0 if 'MariaDB' in x else 1, x))

    for server_name in servers:
        server_data = data[server_name]
        if not server_data['threads']:
            continue

        # Sort by thread count
        sorted_indices = sorted(range(len(server_data['threads'])),
                               key=lambda i: server_data['threads'][i])
        threads = [server_data['threads'][i] for i in sorted_indices]
        values = [server_data[metric][i] for i in sorted_indices]

        color = COLORS.get(server_name, 'gray')
        is_filled = MARKER_FILLED.get(server_name, True)

        # Set transparency for reference servers (MySQL and Percona)
        is_reference = 'MySQL' in server_name or 'Percona' in server_name
        alpha = 0.25 if is_reference else 1.0

        # For outlined markers: face color is white, edge color is the line color, smaller size
        # For filled markers: both face and edge are the line color, larger size
        if is_filled:
            markerfacecolor = color
            markeredgecolor = color
            markeredgewidth = 0
            markersize = 9
        else:
            markerfacecolor = 'white'
            markeredgecolor = color
            markeredgewidth = 2
            markersize = 7

        ax.plot(threads, values,
                marker=MARKER_STYLES.get(server_name, 'o'),
                linestyle=LINE_STYLES.get(server_name, '-'),
                color=color,
                label=server_name,
                linewidth=2.25,
                markersize=markersize,
                markerfacecolor=markerfacecolor,
                markeredgecolor=markeredgecolor,
                markeredgewidth=markeredgewidth,
                alpha=alpha)

    # Title styling - simpler, cleaner
    ax.set_title(f'Sysbench OLTP Read-Write Throughput   [innodb_buffer_pool_size = {mem_tier}B]',
                 fontsize=16, pad=20, color='#333333')

    # Axis labels
    ax.set_xlabel('Client Threads', fontsize=13, color='#333333')
    ax.set_ylabel('Transactions per second (TPS)', fontsize=13, color='#333333')

    # Log scale for x-axis
    ax.set_xscale('log', base=2)
    ax.set_xticks(THREAD_COUNTS)
    ax.set_xticklabels([str(x) for x in THREAD_COUNTS])

    # Format y-axis with thousands
    ax.yaxis.set_major_formatter(FuncFormatter(thousands_formatter))

    # Start y-axis from 0
    ax.set_ylim(bottom=0)

    # Grid styling - subtle horizontal lines only
    ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.8, color='#CCCCCC')
    ax.grid(False, axis='x')

    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#CCCCCC')
    ax.spines['bottom'].set_color('#CCCCCC')

    # Tick styling
    ax.tick_params(axis='both', which='major', labelsize=11, colors='#666666')

    # Legend styling - inside plot area, top left
    legend = ax.legend(loc='upper left', frameon=True,
                      fancybox=False, shadow=False,
                      fontsize=11, edgecolor='#CCCCCC',
                      framealpha=0.95, borderpad=1)
    legend.get_frame().set_linewidth(1)

    plt.tight_layout()

    return plt


def main():
    """Main function to generate all graphs."""
    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Collecting benchmark data...")
    data = collect_data()

    if not data:
        print("Error: No data collected. Check benchmark logs directory.")
        return

    print(f"Generating graphs in {OUTPUT_DIR}...")

    for mem_tier in MEMORY_TIERS:
        if mem_tier not in data:
            print(f"Warning: No data for memory tier {mem_tier}")
            continue

        print(f"  Processing {mem_tier}B memory tier...")

        # Generate TPS graph
        plt_tps = create_graph(mem_tier, data[mem_tier], metric='tps')
        tps_filename = OUTPUT_DIR / f"throughput_tps_{mem_tier.lower()}.png"
        plt_tps.savefig(tps_filename, dpi=100, bbox_inches='tight')
        plt.close()
        print(f"    Saved: {tps_filename}")

    print("\nGraph generation complete!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
