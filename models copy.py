# import modules
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON
from typing import Optional

# Define the TradeData model with the following columns:
class TradeData(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    uuid: str
    hash: str = Field(unique=True)  # Add unique constraint
    exchange: str
    asset: str
    strategy_name: str
    timeframe: str
    timerange: str

# Define the BacktestData model with the following columns:
class BacktestData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    avg_stake_amount: float
    backtest_best_day: float
    backtest_best_day_abs: float
    backtest_days: int
    backtest_end: str
    backtest_end_ts: int
    backtest_hash: str
    backtest_run_end_ts: int
    backtest_run_start_ts: int
    backtest_start: str
    backtest_start_ts: int
    backtest_strategy: str
    backtest_uuid: str
    backtest_worst_day: float
    backtest_worst_day_abs: float
    cagr: float
    calmar: float
    canceled_entry_orders: int
    canceled_trade_entries: int
    csum_max: float
    csum_min: float
    draw_days: int
    drawdown_end: str
    drawdown_end_ts: float
    drawdown_start: str
    drawdown_start_ts: float
    draws: int
    dry_run_wallet: float
    enable_protections: bool
    exit_profit_offset: float
    exit_profit_only: bool
    expectancy: float
    expectancy_ratio: float
    final_balance: float
    holding_avg: str
    holding_avg_s: float
    ignore_roi_if_entry_signal: bool
    loser_holding_avg: str
    loser_holding_avg_s: float
    losing_days: int
    losses: int
    market_change: float
    max_consecutive_losses: int
    max_consecutive_wins: int
    max_drawdown_abs: float
    max_drawdown_account: float
    max_drawdown_high: float
    max_drawdown_low: float
    max_open_trades: int
    max_open_trades_setting: int
    max_relative_drawdown: float
    minimal_roi: dict = Field(sa_column=Column(JSON))  # Use JSON for Dict
    pairlist: list = Field(sa_column=Column(JSON))  # Use JSON for List
    profit_factor: float
    profit_mean: float
    profit_median: float
    profit_total: float
    profit_total_abs: float
    profit_total_long: float
    profit_total_long_abs: float
    profit_total_short: float
    profit_total_short_abs: float
    rejected_signals: int
    replaced_entry_orders: int
    sharpe: float
    sortino: float
    stake_amount: str
    stake_currency: str
    stake_currency_decimals: int
    starting_balance: float
    stoploss: float
    strategy_name: str
    timedout_entry_orders: int
    timedout_exit_orders: int
    timeframe: str
    timeframe_detail: str
    timerange: str
    total_trades: int
    total_volume: float
    trade_count_long: int
    trade_count_short: int
    trades_per_day: float
    trailing_only_offset_is_reached: bool
    trailing_stop: bool
    trailing_stop_positive: Optional[float]
    trailing_stop_positive_offset: float
    use_custom_stoploss: bool
    use_exit_signal: bool
    winner_holding_avg: str
    winner_holding_avg_s: float
    winning_days: int
    winrate: float
    wins: int
