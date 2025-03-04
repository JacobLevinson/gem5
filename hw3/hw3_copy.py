import os
import shutil

# Source directory where gem5 results are stored
SOURCE_DIR = "/root/spec2017/results"

# Destination directory where we will copy the selected files
DEST_DIR = "/root/gem5/hw3/results"

# Ensure the destination directory exists
os.makedirs(DEST_DIR, exist_ok=True)

# Iterate over each replacement policy directory (LRURP, NRURP, etc.)
for policy in os.listdir(SOURCE_DIR):
    policy_path = os.path.join(SOURCE_DIR, policy)
    
    # Ensure it's a directory
    if not os.path.isdir(policy_path):
        continue
    
    # Create the same policy directory in the destination
    dest_policy_path = os.path.join(DEST_DIR, policy)
    os.makedirs(dest_policy_path, exist_ok=True)

    # Iterate over each benchmark directory (lbm_s, nab_s, etc.)
    for benchmark in os.listdir(policy_path):
        benchmark_path = os.path.join(policy_path, benchmark)
        
        # Ensure it's a directory
        if not os.path.isdir(benchmark_path):
            continue
        
        # Create the same benchmark directory in the destination
        dest_benchmark_path = os.path.join(dest_policy_path, benchmark)
        os.makedirs(dest_benchmark_path, exist_ok=True)

        # Paths to the files we need
        stats_file = os.path.join(benchmark_path, "m5out", "stats.txt")
        config_file = os.path.join(benchmark_path, "m5out", "config.ini")

        # Copy files if they exist
        for file_path in [stats_file, config_file]:
            if os.path.exists(file_path):
                shutil.copy(file_path, dest_benchmark_path)

print(f"Results copied to {DEST_DIR} successfully!")
