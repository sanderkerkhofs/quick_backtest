-- SQL script to create tables for backtest data

-- Drop tables if they already exist
DROP TABLE IF EXISTS periodic_breakdown;
DROP TABLE IF EXISTS exit_reason_summary;
DROP TABLE IF EXISTS daily_profit;
DROP TABLE IF EXISTS trades;
DROP TABLE IF EXISTS strategies;

-- Create strategies table
CREATE TABLE strategies (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    total_trades INT,
    wins INT,
    losses INT,
    draws INT,
    winrate DECIMAL(5, 2),
    best_day_abs DECIMAL(10, 2),
    worst_day_abs DECIMAL(10, 2),
    backtest_best_day DECIMAL(10, 2),
    backtest_worst_day DECIMAL(10, 2)
);

-- Create trades table
CREATE TABLE trades (
    id SERIAL PRIMARY KEY,
    strategy_id INT REFERENCES strategies(id),
    pair VARCHAR(50),
    stake_amount DECIMAL(15, 4),
    max_stake_amount DECIMAL(15, 4),
    amount DECIMAL(15, 4),
    open_date TIMESTAMP WITH TIME ZONE,
    close_date TIMESTAMP WITH TIME ZONE,
    open_rate DECIMAL(10, 4),
    close_rate DECIMAL(10, 4),
    fee_open DECIMAL(10, 4),
    fee_close DECIMAL(10, 4),
    trade_duration INT,
    profit_ratio DECIMAL(10, 10),
    profit_abs DECIMAL(15, 4),
    exit_reason VARCHAR(255),
    initial_stop_loss_abs DECIMAL(10, 2),
    initial_stop_loss_ratio DECIMAL(10, 2)
);

-- Create daily profit table
CREATE TABLE daily_profit (
    id SERIAL PRIMARY KEY,
    strategy_id INT REFERENCES strategies(id),
    date DATE,
    profit_abs DECIMAL(15, 4)
);

-- Create exit reason summary table
CREATE TABLE exit_reason_summary (
    id SERIAL PRIMARY KEY,
    strategy_id INT REFERENCES strategies(id),
    exit_reason VARCHAR(255),
    trades INT,
    profit_mean DECIMAL(10, 10)
);

-- Create periodic breakdown table
CREATE TABLE periodic_breakdown (
    id SERIAL PRIMARY KEY,
    strategy_id INT REFERENCES strategies(id),
    period_type VARCHAR(50), -- e.g., 'day', 'week', 'month'
    date DATE,
    profit_abs DECIMAL(15, 4),
    wins INT
);