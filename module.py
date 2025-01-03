# import modules
import docker
import re
import json
import os
from config import *

# Initialize Docker client
client = docker.from_env()

# Helper function to check timeframe
def check_timeframe(strategy_file, timeframe):
    """Return provided timeframe or extract from strategy file."""
    if timeframe != "strategy_default":
        return timeframe

    try:
        with open(strategy_file, 'r') as file:
            content = file.read()

        # Search for timeframe or ticker_interval
        match = re.search(r'\b(timeframe|ticker_interval)\s*=\s*[\'\"]?([\w\d]+)[\'\"]?', content)
        if match:
            return match.group(2)

        raise ValueError(f"No valid timeframe or ticker_interval found in {strategy_file}")

    except FileNotFoundError:
        raise FileNotFoundError(f"Strategy file not found: {strategy_file}")
    except Exception as e:
        raise RuntimeError(f"Error reading {strategy_file}: {str(e)}")

def list_strategy_folder(folder):
    """Read all Python files in a folder and return a list of file names."""
    files = []
    for file in os.listdir(folder):
        if file.endswith(".py"):
            files.append(os.path.splitext(file)[0])
    return files

def download_data(pair_list, exchange, data_format, timeframe, timerange):
    """Download market data using Freqtrade."""
    pairs = ' '.join(pair_list)

    download_command = (
        f"download-data "
        f"--data-format-ohlcv {data_format} "
        f"--pairs {pairs} "
        f"--exchange {exchange} "
        f"--timerange={timerange} "
        f"--timeframe {timeframe} "
    )

    try:
        container = client.containers.run(
            image=DOCKER_IMAGE_NAME,
            command=download_command,
            detach=True,
            remove=True,
            tty=True,
            volumes={
                LOCAL_DATA_DIR: {"bind": REMOTE_DATA_DIR, "mode": "rw"},
                LOCAL_STRATEGY_DIR: {"bind": REMOTE_STRATEGY_DIR, "mode": "rw"},
                LOCAL_CONFIG_DIR: {"bind": REMOTE_CONFIG_DIR, "mode": "rw"},
                LOCAL_RESULTS_DIR: {"bind": REMOTE_RESULTS_DIR, "mode": "rw"},
            },
        )
        exit_code = container.wait()
        logs = container.logs().decode()

        if exit_code['StatusCode'] != 0:
            raise RuntimeError(f"Data download failed. Logs: {logs}")

        return logs

    except docker.errors.DockerException as e:
        raise RuntimeError(f"Docker error: {e}")

def run_backtest(pair_list, strategy_name, data_format, timerange, timeframe, max_open_trades):
    """Run a backtest using Freqtrade."""
    pairs = ' '.join(pair_list)

    backtest_command = (
        f"backtesting "
        f"--config {REMOTE_CONFIG_DIR}{CONFIG_FILE} "
        f"--data-format-ohlcv {data_format} "
        f"--pairs {pairs} "
        f"--strategy {strategy_name} "
        f"--timerange={timerange} "
        f"--timeframe {timeframe} "
        f"--max-open-trades {max_open_trades} "
    )

    try:
        container = client.containers.run(
            image=DOCKER_IMAGE_NAME,
            command=backtest_command,
            detach=True,
            remove=True,
            tty=True,
            volumes={
                LOCAL_DATA_DIR: {"bind": REMOTE_DATA_DIR, "mode": "rw"},
                LOCAL_STRATEGY_DIR: {"bind": REMOTE_STRATEGY_DIR, "mode": "rw"},
                LOCAL_CONFIG_DIR: {"bind": REMOTE_CONFIG_DIR, "mode": "rw"},
                LOCAL_RESULTS_DIR: {"bind": REMOTE_RESULTS_DIR, "mode": "rw"},
            },
        )
        exit_code = container.wait()
        logs = container.logs().decode()

        if exit_code['StatusCode'] != 0:
            raise RuntimeError(f"Backtest failed. Logs: {logs}")

        return logs

    except docker.errors.DockerException as e:
        raise RuntimeError(f"Docker error: {e}")
    
def read_latest_backtest(results_dir, backtest_uuid=None, backtest_hash=None):
    # Set default file path
    file_path = os.path.join(results_dir, ".last_result.json")

    # Open last_result.json
    with open(file_path) as file:
        latest_backtest_filename = json.load(file)["latest_backtest"]

    # Read latest backtest
    backtest_file_path = os.path.join(results_dir, latest_backtest_filename)
    if os.path.exists(backtest_file_path):
        with open(backtest_file_path) as backtest_file:
            backtest_json = json.load(backtest_file)

    # Get the first key (assuming it's the name)
    backtest_strategy = list(backtest_json['strategy'].keys())[0]

    # Extract Strategy Overview
    backtest_data = backtest_json['strategy'][backtest_strategy]

    # Add backtest_strategy, backtest_uuid and backtest_hash
    backtest_data['backtest_strategy'] = backtest_strategy
    backtest_data['backtest_uuid'] = backtest_uuid
    backtest_data['backtest_hash'] = backtest_hash

    # Remove unused keys
    keys_to_remove = [
        'best_pair', 'daily_profit', 'exit_reason_summary', 'left_open_trades',
        'periodic_breakdown', 'results_per_enter_tag', 'results_per_pair',
        'trades', 'worst_pair', 'locks'
    ]
    for key in keys_to_remove:
        backtest_data.pop(key, None)

    
    # Filter out unsupported fields from backtest_data
    filtered_dict = {}
    for k, v in backtest_data.items():  # Ensure you're filtering backtest_data
        if not isinstance(v, (list, dict)):
            filtered_dict[k] = v

    return backtest_data