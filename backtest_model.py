from sqlmodel import SQLModel, Field
from typing import Optional

class BacktestSimple(SQLModel, table=True):
    avg_stake_amount: Optional[float] = Field(default=None)
    backtest_best_day: Optional[float] = Field(default=None)
    backtest_best_day_abs: Optional[float] = Field(default=None)
    backtest_days: Optional[int] = Field(default=None)
    backtest_end: Optional[str] = Field(default=None)  # Consider using datetime if you want to parse it
    backtest_end_ts: Optional[int] = Field(default=None)
    backtest_hash: Optional[str] = Field(default=None)
    backtest_run_end_ts: Optional[int] = Field(default=None)
    backtest_run_start_ts: Optional[int] = Field(default=None)
    backtest_start: Optional[str] = Field(default=None)  # Consider using datetime if you want to parse it
    backtest_start_ts: Optional[int] = Field(default=None)
    backtest_strategy: Optional[str] = Field(default=None)
    backtest_uuid: Optional[str] = Field(default=None)
    backtest_worst_day: Optional[float] = Field(default=None)
    backtest_worst_day_abs: Optional[float] = Field(default=None)
    cagr: Optional[float] = Field(default=None)
    calmar: Optional[float] = Field(default=None)
    canceled_entry_orders: Optional[int] = Field(default=None)
    canceled_trade_entries: Optional[int] = Field(default=None)
    csum_max: Optional[float] = Field(default=None)
    csum_min: Optional[float] = Field(default=None)
    draw_days: Optional[int] = Field(default=None)
    drawdown_end: Optional[str] = Field(default=None)  # Consider using datetime if you want to parse it
    drawdown_end_ts: Optional[float] = Field(default=None)
    drawdown_start: Optional[str] = Field(default=None)  # Consider using datetime if you want to parse it
    drawdown_start_ts: Optional[float] = Field(default=None)
    draws: Optional[int] = Field(default=None)
    dry_run_wallet: Optional[float] = Field(default=None)
    enable_protections: Optional[bool] = Field(default=None)
    exit_profit_offset: Optional[float] = Field(default=None)
    exit_profit_only: Optional[bool] = Field(default=None)
    expectancy: Optional[float] = Field(default=None)
    expectancy_ratio: Optional[float] = Field(default=None)
    final_balance: Optional[float] = Field(default=None)
    holding_avg: Optional[str] = Field(default=None)  # Consider using a suitable type for duration
    holding_avg_s: Optional[float] = Field(default=None)
    ignore_roi_if_entry_signal: Optional[bool] = Field(default=None)
    loser_holding_avg: Optional[str] = Field(default=None)  # Consider using a suitable type for duration
    loser_holding_avg_s: Optional[float] = Field(default=None)
    losing_days: Optional[int] = Field(default=None)