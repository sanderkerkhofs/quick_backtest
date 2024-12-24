import docker
import re
import json
import os

# Define file paths for configuration and data directories
LOCAL_DATA_DIR = "/home/ubuntu/_DATA/"
REMOTE_DATA_DIR = "/freqtrade/user_data/data/"
LOCAL_STRATEGY_DIR = "/home/ubuntu/_STRATEGIES/TESTED/"
REMOTE_STRATEGY_DIR = "/freqtrade/user_data/strategies/"
LOCAL_CONFIG_DIR = "/home/ubuntu/_CONFIGS/"
REMOTE_CONFIG_DIR = "/freqtrade/user_data/config/"
LOCAL_RESULTS_DIR = "/home/ubuntu/_BACKTEST_RESULTS/"
REMOTE_RESULTS_DIR = "/freqtrade/user_data/backtest_results/"

DOCKER_IMAGE_NAME = "sanderke123/freqtrade2"
CONFIG_FILE = "config_backtest.json"

# Initialize Docker client
client = docker.from_env()

def check_strategy_timeframe(strategy_file):
    """Check a single strategy file for timeframe or ticker_interval."""
    with open(strategy_file, 'r') as file:
        content = file.read()

        # Search for timeframe and ticker_interval using regex
        timeframe_match = re.search(r'\btimeframe\s*=\s*([\'"]?)(.*?)\1', content)
        ticker_interval_match = re.search(r'\bticker_interval\s*=\s*([\'"]?)(.*?)\1', content)

        if timeframe_match:
            return timeframe_match.group(2)
        if ticker_interval_match:
            return ticker_interval_match.group(2)

    raise ValueError(f"No valid timeframe or ticker_interval found in {strategy_file}")

def download_data(pair_list, exchange, data_format, timerange, strategy_name):
    """Download market data using Freqtrade."""
    timeframe = check_strategy_timeframe(f"{LOCAL_STRATEGY_DIR}{strategy_name}.py")
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

def run_backtest(pair_list, strategy_name, data_format, timerange, max_open_trades):
    """Run a backtest using Freqtrade."""
    pairs = ' '.join(pair_list)

    backtest_command = (
        f"backtesting "
        f"--config {REMOTE_CONFIG_DIR}{CONFIG_FILE} "
        f"--data-format-ohlcv {data_format} "
        f"--pairs {pairs} "
        f"--strategy {strategy_name} "
        f"--timerange={timerange} "
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
    
def read_latest_backtest(script_dir="/home/ubuntu/_BACKTEST_RESULTS"):
    file_path = os.path.join(script_dir, ".last_result.json")

    # Open last_result.json
    with open(file_path) as file:
        latest_backtest_filename = json.load(file)["latest_backtest"]

    # Read latest backtest
    backtest_file_path = os.path.join(script_dir, latest_backtest_filename)
    if os.path.exists(backtest_file_path):
        with open(backtest_file_path) as backtest_file:
            backtest_json = json.load(backtest_file)

    # Get the first key (assuming it's the name)
    backtest_strategy = list(backtest_json['strategy'].keys())[0]

    # Extract Strategy Overview
    backtest_data = backtest_json['strategy'][backtest_strategy]

    # Add strategy name
    backtest_data['strategy_name'] = backtest_strategy

    # Remove unused keys
    keys_to_remove = [
        'best_pair', 'daily_profit', 'exit_reason_summary', 'left_open_trades',
        'periodic_breakdown', 'results_per_enter_tag', 'results_per_pair',
        'trades', 'worst_pair', 'locks'
    ]
    for key in keys_to_remove:
        backtest_data.pop(key, None)

    return backtest_data

# Examples
if __name__ == "__main__":


    # # Example: Download market data
    # try:
    #     print("Downloading data...")
    #     download_logs = download_data(
    #         pair_list=["BTC/USDT", "ETH/USDT"],
    #         exchange="binance",
    #         data_format="json",
    #         timerange="20240101-20241101",
    #         strategy_name="RSI"
    #     )
    #     print("Download logs:")
    #     print(download_logs)
    # except Exception as e:
    #     print(f"Error: {e}")

    # # Example: Run backtest
    # try:
    #     print("Running backtest...")
    #     backtest_logs = run_backtest(
    #         pair_list=["BTC/USDT", "ETH/USDT"],
    #         strategy_name="RSI",
    #         data_format="json",
    #         timerange="20240101-20241101",
    #         max_open_trades=3
    #     )
    #     print("Backtest logs:")
    #     print(backtest_logs)
    # except Exception as e:
    #     print(f"Error: {e}")

    # Example: Load backtest result
    try:
        print("Loading backtest result...")
        backtest_result = read_latest_backtest()
        print("Backtest result:")
        print(backtest_result)
    except Exception as e:
        print(f"Error: {e}")
