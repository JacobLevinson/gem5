import os
import shutil
import re
import math
import numpy as np
import matplotlib.pyplot as plt

HW1_RESULTS_DIR = "hw1-results"
HW1_STATS_DIR = "hw1-stats"

# Ensure the hw1-stats directory exists
os.makedirs(HW1_STATS_DIR, exist_ok=True)

# Default configuration (matches your gem5 script defaults)
DEFAULT_CONFIG = {
    "cpu": "DerivO3CPU",
    "width": "8",
    "freq": "2GHz",
    "l2": "2MB",
    "opt": "-O3-ffast-math-ftree-vectorize",  # Note: no spaces so it matches the dir
}

EXPERIMENT_GROUPS = {
    "CPU Type": {"param_name": "cpu", "param_values": ["DerivO3CPU", "X86MinorCPU"]},
    "Issue Width": {"param_name": "width", "param_values": ["8", "2"]},
    "Clock Freq": {"param_name": "freq", "param_values": ["2GHz", "1GHz", "4GHz"]},
    "L2 Cache": {"param_name": "l2", "param_values": ["2MB", "0kB", "256kB", "16MB"]},
    "Compiler Opt": {"param_name": "opt", "param_values": ["-O3-ffast-math-ftree-vectorize", "-O1"]},
}

BENCHMARKS = ["mm", "spmv", "lfsr", "merge", "sieve"]

############################
# Helper functions #
############################

def parse_config_from_dirname(dirname):
    parts = dirname.split("_")
    if len(parts) < 6:
        return None

    benchmark = parts[0]

    def get_val(prefix, item_list):
        for item in item_list:
            if item.startswith(prefix + "-"):
                return item.split(prefix + "-")[-1]
        return None

    cpu_val = get_val("cpu", parts)
    width_val = get_val("width", parts)
    freq_val = get_val("freq", parts)
    l2_val = get_val("l2", parts)

    opt_string = None
    for p in parts:
        if p.startswith("opt-"):
            idx = parts.index(p)
            opt_string = "_".join(parts[idx:]).split("opt-")[-1]
            break

    if not all([benchmark, cpu_val, width_val, freq_val, l2_val, opt_string]):
        return None

    return {
        "benchmark": benchmark,
        "cpu": cpu_val,
        "width": width_val,
        "freq": freq_val,
        "l2": l2_val,
        "opt": opt_string,
    }

def get_ipc_from_stats(stats_file):
    if not os.path.isfile(stats_file):
        return None

    with open(stats_file, "r") as f:
        for line in f:
            if "system.cpu.ipc" in line:
                fields = line.strip().split()
                if len(fields) >= 2:
                    try:
                        return float(fields[1])
                    except ValueError:
                        return None
    return None

#####################################
# Copy config.ini and stats.txt files
#####################################

def copy_and_rename_files():
    all_dirs = sorted(os.listdir(HW1_RESULTS_DIR))

    for d in all_dirs:
        config_info = parse_config_from_dirname(d)
        if config_info is None:
            print(f"[WARNING] Could not parse config from {d}, skipping.")
            continue

        experiment_name = f"{config_info['cpu']}_width-{config_info['width']}_freq-{config_info['freq']}_l2-{config_info['l2']}_opt-{config_info['opt']}"
        benchmark_name = config_info["benchmark"]

        # Prepare source and destination file paths
        config_file = os.path.join(HW1_RESULTS_DIR, d, "config.ini")
        stats_file = os.path.join(HW1_RESULTS_DIR, d, "stats.txt")

        if os.path.exists(config_file):
            new_config_name = f"{benchmark_name}_{experiment_name}_config.ini"
            shutil.copy(config_file, os.path.join(HW1_STATS_DIR, new_config_name))
        
        if os.path.exists(stats_file):
            new_stats_name = f"{benchmark_name}_{experiment_name}_stats.txt"
            shutil.copy(stats_file, os.path.join(HW1_STATS_DIR, new_stats_name))

    print(f"All config.ini and stats.txt files copied to {HW1_STATS_DIR}")

copy_and_rename_files()

###################################
# Gather IPC results from all dirs #
###################################

results = {}

all_dirs = sorted(os.listdir(HW1_RESULTS_DIR))
for d in all_dirs:
    stats_path = os.path.join(HW1_RESULTS_DIR, d, "stats.txt")
    if not os.path.isfile(stats_path):
        print(f"[WARNING] No stats.txt found in {d}, skipping.")
        continue

    config_info = parse_config_from_dirname(d)
    if config_info is None:
        print(f"[WARNING] Could not parse config from {d}, skipping.")
        continue

    ipc_val = get_ipc_from_stats(stats_path)
    if ipc_val is None:
        print(f"[WARNING] IPC not found in {stats_path}, skipping.")
        continue

    cfg_key = (
        config_info["cpu"],
        config_info["width"],
        config_info["freq"],
        config_info["l2"],
        config_info["opt"],
    )
    benchmark = config_info["benchmark"]

    if cfg_key not in results:
        results[cfg_key] = {}
    results[cfg_key][benchmark] = ipc_val

############################
# Compute harmonic means  #
############################

def harmonic_mean(values):
    """
    Compute the harmonic mean of a list of numbers,
    ignoring zeros or negative values to avoid division errors.
    """
    filtered = [v for v in values if v > 0]
    if not filtered:
        return 0.0
    return len(filtered) / sum((1.0 / x) for x in filtered)

config_hmean_ipc = {}
for cfg_key, bm_ipcs in results.items():
    gm_ipc = harmonic_mean(list(bm_ipcs.values()))
    config_hmean_ipc[cfg_key] = gm_ipc

############################
# Plotting grouped bar charts
############################

OUTDIR = "figures_ipc"
os.makedirs(OUTDIR, exist_ok=True)

for exp_name, info in EXPERIMENT_GROUPS.items():
    param_name = info["param_name"]
    param_values = info["param_values"]

    grouped_data = []
    for val in param_values:
        cfg = DEFAULT_CONFIG.copy()
        cfg[param_name] = val
        cfg_key = (cfg["cpu"], cfg["width"], cfg["freq"], cfg["l2"], cfg["opt"])
        
        subbar_values = [results.get(cfg_key, {}).get(bm, 0.0) for bm in BENCHMARKS]
        subbar_values.append(config_hmean_ipc.get(cfg_key, 0.0))
        grouped_data.append(subbar_values)

    x_positions = np.arange(len(param_values))
    fig, ax = plt.subplots(figsize=(9, 5))

    for j, bm in enumerate(BENCHMARKS + ["hmean"]):
        offset = j - 2.5
        x_sub = x_positions + (offset * 0.15)
        heights = [grouped_data[i][j] for i in range(len(param_values))]
        ax.bar(x_sub, heights, width=0.15, label=bm)

    ax.set_xticks(x_positions)
    ax.set_xticklabels(param_values, rotation=0, ha="center")
    ax.set_ylabel("IPC")
    ax.set_title(f"Benchmarks & hmean for {exp_name}")
    ax.legend(title="Legend", loc="best")

    plt.tight_layout()
    plt.savefig(os.path.join(OUTDIR, f"{exp_name.replace(' ', '_')}.png"), dpi=150)
    plt.close(fig)

print("All plots generated in the 'figures_ipc' directory!")
