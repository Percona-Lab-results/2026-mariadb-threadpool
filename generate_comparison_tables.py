#!/usr/bin/env python3
"""
Generate comparison tables for MariaDB vs MySQL/Percona in section 3.1.
Creates colored tables with bars showing relative performance.
"""

import os
import re
from pathlib import Path
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import matplotlib.patches as mpatches
import numpy as np

# Configuration
BENCHMARK_DIR = Path(__file__).parent / "benchmark_logs"
OUTPUT_DIR = Path(__file__).parent / "graphs_out"

# Server configurations (non-thread-pool only for primary comparison)
SERVER_MAPPING = {
    'mariadb/11.8.6-MariaDB-ubu2404': 'MariaDB 11.8.6',
    'mariadb/12.2.2-MariaDB-ubu2404': 'MariaDB 12.2.2',
    'mysql/8.4.8': 'MySQL 8.4.8',
    'mysql/9.7.0-er2': 'MySQL 9.7.0',
    'percona/8.4.8-8': 'Percona Server 8.4.8',
}

def parse_sysbench_file(filepath):
    """Extract TPS from sysbench output file."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()

        tps_match = re.search(r'transactions:\s+\d+\s+\((\d+\.?\d*)\s+per sec\.\)', content)

        if tps_match:
            return float(tps_match.group(1))
        else:
            print(f"Warning: Could not parse {filepath}")
            return None
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return None


def collect_specific_data(scenarios):
    """
    Collect data for specific scenarios.
    scenarios: list of tuples (mem_tier, threads)
    Returns: dict[server_name] = {scenario: tps}
    """
    data = defaultdict(dict)

    for server_path, server_name in SERVER_MAPPING.items():
        server_dir = BENCHMARK_DIR / server_path
        if not server_dir.exists():
            print(f"Warning: {server_dir} does not exist, skipping")
            continue

        for mem_tier, threads in scenarios:
            filename = f"Tier{mem_tier}_RW_{threads}th.sysbench.txt"
            filepath = server_dir / filename

            if filepath.exists():
                tps = parse_sysbench_file(filepath)
                if tps is not None:
                    scenario_key = f"{mem_tier}_{threads}t"
                    data[server_name][scenario_key] = tps

    return data


def create_comparison_table(title, scenarios, data, filename):
    """
    Create a comparison table for specific scenarios.
    scenarios: list of tuples (mem_tier, threads, label)
    """
    # Prepare server order
    servers = ['MariaDB 11.8.6', 'MariaDB 12.2.2', 'MySQL 8.4.8', 'MySQL 9.7.0', 'Percona Server 8.4.8']

    # Create matrix of TPS values
    tps_matrix = []
    scenario_labels = []

    for mem_tier, threads, label in scenarios:
        scenario_key = f"{mem_tier}_{threads}t"
        scenario_labels.append(label)

        row = []
        for server in servers:
            tps = data.get(server, {}).get(scenario_key, 0)
            row.append(tps)
        tps_matrix.append(row)

    if not tps_matrix:
        return None

    tps_array = np.array(tps_matrix).T  # Transpose: servers as rows, scenarios as columns

    # Column background colors
    col_bg_colors = [
        '#E8F4F8',  # Light blue
        '#E8F8E8',  # Light green
        '#FFF4E0',  # Light orange
        '#F8E8F8',  # Light purple
        '#E0F8F8',  # Light cyan
    ]

    # Header colors
    col_header_colors = [
        '#B3D9E8',  # Saturated blue
        '#B3E8B3',  # Saturated green
        '#FFE0A0',  # Saturated orange
        '#E8B3E8',  # Saturated purple
        '#A0E8E8',  # Saturated cyan
    ]

    # Create figure
    n_rows = len(servers)
    n_cols = len(scenarios)

    fig = plt.figure(figsize=(16, n_rows * 0.7 + 2.5), dpi=100)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_subplot(111)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Calculate dimensions
    table_height = 0.78
    table_bottom = 0.02
    table_top = table_bottom + table_height

    row_label_width = 0.28
    col_width = (1.0 - row_label_width) / n_cols
    row_height = table_height / (n_rows + 1)  # +1 for header

    start_y = table_top
    start_x = row_label_width

    # Draw title
    ax.text(0.5, 0.95, title, ha='center', va='center', fontsize=18, fontweight='bold')

    # Draw header row
    for col_idx, label in enumerate(scenario_labels):
        x = start_x + col_idx * col_width
        y = start_y

        header_color = col_header_colors[col_idx % len(col_header_colors)]
        rect = mpatches.Rectangle((x, y), col_width, row_height,
                                 facecolor=header_color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + col_width/2, y + row_height/2, label,
               ha='center', va='center', fontweight='bold', fontsize=14)

    # Draw "Server" label
    rect = mpatches.Rectangle((0, start_y), row_label_width, row_height,
                             facecolor='#D0E0F0', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(row_label_width/2, start_y + row_height/2, 'Server',
           ha='center', va='center', fontweight='bold', fontsize=16)

    # Draw data rows
    for row_idx, server in enumerate(servers):
        y = start_y - (row_idx + 1) * row_height

        # Draw row label (server name)
        label_bg = '#E8F4E8' if 'MariaDB' in server else '#F0F0F0'
        rect = mpatches.Rectangle((0, y), row_label_width, row_height,
                                 facecolor=label_bg, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(0.01, y + row_height/2, server,
               ha='left', va='center', fontweight='bold', fontsize=14)

        # Draw data cells with bars
        for col_idx in range(n_cols):
            x = start_x + col_idx * col_width
            value = tps_array[row_idx, col_idx]

            # Column background
            bg_color = col_bg_colors[col_idx % len(col_bg_colors)]
            rect = mpatches.Rectangle((x, y), col_width, row_height,
                                     facecolor=bg_color, edgecolor='black', linewidth=1.5)
            ax.add_patch(rect)

            if value == 0:
                ax.text(x + col_width/2, y + row_height/2, '—',
                       ha='center', va='center', fontsize=10)
                continue

            # Calculate bar size as proportion of max value in column
            col_values = tps_array[:, col_idx]
            col_values = col_values[col_values > 0]

            if len(col_values) > 0:
                vmin, vmax = col_values.min(), col_values.max()
                norm_value = value / vmax if vmax > 0 else 1.0

                if vmax > vmin:
                    color_norm = (value - vmin) / (vmax - vmin)
                else:
                    color_norm = 1.0
            else:
                norm_value = 1.0
                color_norm = 1.0

            # Color gradient: red (worst) -> yellow (mid) -> green (best)
            if color_norm < 0.5:
                r, g, b = 1.0, color_norm * 2, 0.0
            else:
                r, g, b = 1.0 - (color_norm - 0.5) * 2, 1.0, 0.0

            # Draw bar
            bar_max_width = col_width * 0.85
            bar_x = x + 0.05 * col_width
            bar_y = y + row_height * 0.3
            bar_height_val = row_height * 0.15

            bar_width = norm_value * bar_max_width
            bar_rect = mpatches.Rectangle((bar_x, bar_y), bar_width, bar_height_val,
                                         facecolor=(r, g, b, 0.8),
                                         edgecolor='none')
            ax.add_patch(bar_rect)

            # Draw text value
            ax.text(x + col_width/2, y + row_height * 0.65, f'{int(value):,}',
                   ha='center', va='center', fontsize=13, fontweight='normal')

    return fig


def main():
    """Main function to generate comparison tables."""
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Generating comparison tables for section 3.1...")

    # All thread counts
    thread_counts = [1, 4, 16, 32, 64, 128, 256, 512]

    # Comparison graph generation disabled - using detailed graphs from section 8 instead
    print("\nComparison table generation skipped (using detailed graphs from section 8)")


if __name__ == '__main__':
    main()
