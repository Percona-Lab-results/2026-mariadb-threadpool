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
import matplotlib.patches as mpatches
import numpy as np

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

        # All lines are now non-transparent
        alpha = 1.0

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

    # Title styling - larger, bold
    ax.set_title(f'Sysbench OLTP Read-Write Throughput   [innodb_buffer_pool_size = {mem_tier}B]',
                 fontsize=20, fontweight='bold', pad=20, color='#333333')

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


def create_heatmap_table(mem_tier, data):
    """Create a heatmap table showing TPS values for all servers and thread counts."""
    # Prepare data matrix
    servers = sorted(data.keys(), key=lambda x: (0 if 'MariaDB' in x else 1, x))
    thread_counts = THREAD_COUNTS

    # Create matrix of TPS values
    tps_matrix = []
    server_labels = []

    for server in servers:
        server_data = data[server]
        if not server_data['threads']:
            continue

        # Create a mapping of thread count to TPS
        tps_map = dict(zip(server_data['threads'], server_data['tps']))
        row = [tps_map.get(tc, 0) for tc in thread_counts]
        tps_matrix.append(row)
        server_labels.append(server)

    if not tps_matrix:
        return None

    tps_array = np.array(tps_matrix)

    # Column background colors (different pastel color for each thread count)
    col_bg_colors = [
        '#E8F4F8',  # Light blue
        '#E8F8E8',  # Light green
        '#FFF4E0',  # Light orange
        '#F8E8F8',  # Light purple
        '#E0F8F8',  # Light cyan
        '#FFE8E8',  # Light red
        '#E8E8FF',  # Light blue-purple
        '#F0FFE8',  # Light yellow-green
    ]

    # Header colors (more saturated versions of column backgrounds)
    col_header_colors = [
        '#B3D9E8',  # Saturated blue
        '#B3E8B3',  # Saturated green
        '#FFE0A0',  # Saturated orange
        '#E8B3E8',  # Saturated purple
        '#A0E8E8',  # Saturated cyan
        '#FFB3B3',  # Saturated red
        '#B3B3FF',  # Saturated blue-purple
        '#D0FFB3',  # Saturated yellow-green
    ]

    # Create figure - 1600px width at 100 DPI = 16 inches
    fig = plt.figure(figsize=(16, len(server_labels) * 0.7 + 2.5), dpi=100)
    # Remove all margins/padding
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax = fig.add_subplot(111)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # Calculate dimensions
    n_rows = len(server_labels)
    n_cols = len(thread_counts)

    # Table occupies bottom 80% of figure, title in top 20%
    table_height = 0.78
    table_bottom = 0.02
    table_top = table_bottom + table_height

    row_label_width = 0.28  # Width for server names column
    col_width = (1.0 - row_label_width) / n_cols
    row_height = table_height / (n_rows + 1)  # +1 for header

    start_y = table_top  # Start table header at top of table area
    start_x = row_label_width

    # Draw title well above the table
    title = f'TPS by Thread Count, {mem_tier}B Buffer Pool (Read-Write, Local)'
    ax.text(0.5, 0.95, title, ha='center', va='center', fontsize=18, fontweight='bold')

    # Draw header row
    for col_idx, tc in enumerate(thread_counts):
        x = start_x + col_idx * col_width
        y = start_y

        header_color = col_header_colors[col_idx % len(col_header_colors)]
        rect = mpatches.Rectangle((x, y), col_width, row_height,
                                 facecolor=header_color, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(x + col_width/2, y + row_height/2, f'{tc}t',
               ha='center', va='center', fontweight='bold', fontsize=16)

    # Draw "Engine" label
    rect = mpatches.Rectangle((0, start_y), row_label_width, row_height,
                             facecolor='#D0E0F0', edgecolor='black', linewidth=2)
    ax.add_patch(rect)
    ax.text(row_label_width/2, start_y + row_height/2, 'Engine',
           ha='center', va='center', fontweight='bold', fontsize=16)

    # Draw data rows
    for row_idx, server in enumerate(server_labels):
        y = start_y - (row_idx + 1) * row_height

        # Draw row label (server name)
        label_bg = '#E8F4E8' if 'MariaDB' in server else '#F0F0F0'
        rect = mpatches.Rectangle((0, y), row_label_width, row_height,
                                 facecolor=label_bg, edgecolor='black', linewidth=2)
        ax.add_patch(rect)
        ax.text(0.01, y + row_height/2, server,
               ha='left', va='center', fontweight='bold', fontsize=16)

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
                # Bar size is directly proportional to value relative to max
                norm_value = value / vmax if vmax > 0 else 1.0

                # Calculate ranking within this column (1 = best/highest)
                sorted_col = sorted(col_values, reverse=True)
                rank = sorted_col.index(value) + 1

                # Bar color based on ranking (min to max range)
                if vmax > vmin:
                    color_norm = (value - vmin) / (vmax - vmin)
                else:
                    color_norm = 1.0  # All same, make green
            else:
                norm_value = 1.0
                color_norm = 1.0
                rank = 1

            # Color gradient: red (worst/min) -> yellow (mid) -> green (best/max)
            if color_norm < 0.5:
                r, g, b = 1.0, color_norm * 2, 0.0
            else:
                r, g, b = 1.0 - (color_norm - 0.5) * 2, 1.0, 0.0

            # Draw bar proportional to value (moved down)
            bar_max_width = col_width * 0.85
            bar_x = x + 0.05 * col_width
            bar_y = y + row_height * 0.22  # Moved down from 0.3 to 0.22
            bar_height = row_height * 0.15

            bar_width = norm_value * bar_max_width
            bar_color = (r, g, b)
            bar_rect = mpatches.Rectangle((bar_x, bar_y), bar_width, bar_height,
                                         facecolor=(r, g, b, 0.8),
                                         edgecolor='none')
            ax.add_patch(bar_rect)

            # Draw small rectangle in top-right corner with bar color (moved slightly inward)
            rank_box_width = col_width * 0.15
            rank_box_height = row_height * 0.35
            rank_box_x = x + col_width - rank_box_width - col_width * 0.03  # Move left by 3% of column width
            rank_box_y = y + row_height - rank_box_height - row_height * 0.05  # Move down by 5% of row height

            rank_box = mpatches.Rectangle((rank_box_x, rank_box_y), rank_box_width, rank_box_height,
                                         facecolor=bar_color, edgecolor='none', alpha=0.8)
            ax.add_patch(rank_box)

            # Draw TPS value in center (moved up, black)
            ax.text(x + col_width/2, y + row_height * 0.58, f'{int(value):,}',
                   ha='center', va='center', fontsize=15, fontweight='normal', color='black')

            # Create much darker version of bar color for ranking text (70% darker)
            darker_color = (r * 0.3, g * 0.3, b * 0.3)

            # Draw ranking number in the small rectangle (much darker shade of bar color)
            ax.text(rank_box_x + rank_box_width/2, rank_box_y + rank_box_height/2, str(rank),
                   ha='center', va='center', fontsize=12, fontweight='bold', color=darker_color)

    return fig


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

        # Generate heatmap table
        fig_table = create_heatmap_table(mem_tier, data[mem_tier])
        if fig_table:
            table_filename = OUTPUT_DIR / f"table_tps_{mem_tier.lower()}.png"
            # Save without tight_layout to preserve exact dimensions
            fig_table.savefig(table_filename, dpi=100, bbox_inches=None, facecolor='white')
            plt.close()
            print(f"    Saved: {table_filename}")

    print("\nGraph generation complete!")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == '__main__':
    main()
