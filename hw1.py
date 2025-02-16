import os
import subprocess
from concurrent.futures import ProcessPoolExecutor

# Paths and configurations
gem5_binary = "./build/X86/gem5.opt"
config_script = "configs/deprecated/example/se.py"
benchmark_dir = "./cs251a-microbench"
benchmarks = ["mm", "spmv", "lfsr", "merge", "sieve"]
output_base_dir = "./hw1-results"

# Default configuration
default_config = {
    "cpu": "DerivO3CPU",
    "width": 8,
    "freq": "2GHz",
    "l2_cache": "2MB",
    "opt": "-O3 -ffast-math -ftree-vectorize"
}

# Experiment variations
experiments = [
    {},  # Default configuration
    {"cpu": "X86MinorCPU"},
    {"width": 2},
    {"cpu": "X86MinorCPU", "width": 2},
    {"freq": "1GHz"},
    {"freq": "4GHz"},
    {"l2_cache": "0kB"},
    {"l2_cache": "256kB"},
    {"l2_cache": "16MB"},
    {"opt": "-O1"},
]

# Ensure output directory exists
os.makedirs(output_base_dir, exist_ok=True)
os.chmod(output_base_dir, 0o777)

# Function to run a benchmark
def run_benchmark(benchmark, config):
    # Merge default config with experiment-specific config
    final_config = default_config.copy()
    final_config.update(config)

    unique_dir = os.path.join(output_base_dir, f"{benchmark}_cpu-{final_config['cpu']}_width-{final_config['width']}_freq-{final_config['freq']}_l2-{final_config['l2_cache']}_opt-{final_config['opt'].replace(' ', '')}")


    # Remove previous results to overwrite
    if os.path.exists(unique_dir):
        subprocess.run(f"rm -rf {unique_dir}", shell=True, check=True)

    os.makedirs(unique_dir, exist_ok=True)
    os.chmod(unique_dir, 0o777)

    print(f"Starting: {benchmark}, Config: {final_config}")

    # Copy benchmark files to unique directory
    subprocess.run(f"cp -r {benchmark_dir}/. {unique_dir}/", shell=True, check=True)

    # Ensure Makefile exists before compiling
    makefile_path = os.path.join(unique_dir, "Makefile")
    if not os.path.isfile(makefile_path):
        raise FileNotFoundError(f"Makefile not found in {unique_dir}")

    # Compile the benchmark locally
    make_cmd = f"make -C {unique_dir} clean && make -C {unique_dir} OPT='{final_config['opt']}'"
    subprocess.run(make_cmd, shell=True, check=True)

    # Construct gem5 command
    benchmark_path = os.path.join(unique_dir, benchmark)
    cmd = (
        f"{gem5_binary} --outdir={unique_dir} {config_script} "
        f"--cmd={benchmark_path} "
        f"--cpu-type={final_config['cpu']} "
        f"--cpu-clock={final_config['freq']} "
        f"--mem-type=DDR3_1600_8x8 "
        f"--caches --l1d_size=64kB --l1i_size=64kB "
    )

    if final_config["l2_cache"] != "0kB":
        cmd += f"--l2cache --l2_size={final_config['l2_cache']} "

    if final_config["cpu"] == "DerivO3CPU":
        cmd += (
            f"--param system.cpu[0].issueWidth={final_config['width']} "
            f"--param system.cpu[0].fetchWidth={final_config['width']} "
            f"--param system.cpu[0].decodeWidth={final_config['width']} "
            f"--param system.cpu[0].renameWidth={final_config['width']} "
            f"--param system.cpu[0].dispatchWidth={final_config['width']} "
            f"--param system.cpu[0].wbWidth=8 "
            f"--param system.cpu[0].commitWidth=8 "
            f"--param system.cpu[0].squashWidth=8 "
        )
    elif final_config["cpu"] == "X86MinorCPU":
        cmd += (
            f"--param system.cpu[0].decodeInputWidth={final_config['width']} "
            f"--param system.cpu[0].executeInputWidth={final_config['width']} "
            f"--param system.cpu[0].executeIssueLimit={final_config['width']} "
            f"--param system.cpu[0].executeCommitLimit={final_config['width']} "
        )

    subprocess.run(cmd, shell=True, check=True)
    print(f"Completed: {benchmark}, Config: {final_config}")

# Run all configurations in parallel
with ProcessPoolExecutor() as executor:
    futures = []
    for benchmark in benchmarks:
        for exp in experiments:
            futures.append(executor.submit(run_benchmark, benchmark, exp))

    for future in futures:
        future.result()

print("All experiments completed!")
