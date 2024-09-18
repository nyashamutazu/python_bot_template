# Trading Bot Configuration Guide

This guide explains the configuration settings for the `Bot_01` trading bot. The bot is designed to trade on MetaTrader 5 using customizable risk management, trade execution, and logging mechanisms.

## Bot Metadata

### `bot_name`
- **Description**: The name of your trading bot.
- **Example**: `"Bot_01"`

### `strategy_name`
- **Description**: The strategy the bot uses to generate trade signals.
- **Example**: `"Template"` (can be customized as per the strategy in use).

### `active_status`
- **Description**: Controls whether the bot is currently active or not.
- **Example**: `true` (set to `false` to deactivate the bot).

### `timezone`
- **Description**: The timezone in which the bot will operate. This setting affects the bot’s trading hours.
- **Example**: `"Etc/GMT-2"`

### `sleep_time`
- **Description**: Time (in seconds) the bot will sleep between checks or tasks.
- **Example**: `10` (the bot will sleep for 10 seconds between operations).

### `start_time` & `end_time`
- **Description**: Defines the trading hours for the bot.
- **Example**:
  - `"start_time": "9:00"`
  - `"end_time": "21:00"`

## Risk Management

Risk management settings are critical for controlling how much capital the bot risks on each trade and overall throughout the trading day.

### `max_trade_percentage`
- **Description**: The percentage of account equity that can be risked on a single trade.
- **Example**: `0.01` (1% of the account balance per trade).

### `max_stop_loss_percentage`
- **Description**: The maximum allowable stop loss as a percentage of the account balance.
- **Example**: `0.01` (1% stop loss on the account balance).

### `take_profit_ratio`
- **Description**: The ratio of the take profit to the stop loss. A value of `0.05` indicates a 5:1 reward-to-risk ratio.
- **Example**: `0.05`

### `max_concurrent_trades`
- **Description**: The maximum number of trades the bot can have open at one time.
- **Example**: `3`

### `max_daily_loss_percentage`
- **Description**: The maximum loss the bot can incur in one day before it stops trading.
- **Example**: `0.03` (3% loss on the account balance).

## Error Handling

The bot is configured to handle errors gracefully and retry actions when failures occur.

### `on_error`
- **Description**: Defines the action to take when the bot encounters an error.
- **Example**: `"retry"` (the bot will retry the failed action).

### `max_retries`
- **Description**: Maximum number of times the bot will retry a failed action.
- **Example**: `3`

### `logging_name`
- **Description**: The name of the logging category that will handle error logs.
- **Example**: `"error"`

## Logging

Logging helps track the bot’s activity and errors, which can be useful for debugging and analysis.

### `error`
- **Description**: The logging configuration for errors.
- **Example**:
  ```json
  {
    "name": "error",
    "log_file_path": "/log"
  }
  ```

### `main`
- **Description**: The logging configuration for general bot activity.
- **Example**:
  ```json
  {
    "name": "main",
    "log_file_path": "/log"
  }
  ```

## Signal Management

The bot manages signals to determine whether to process them for trade execution.

### `trade_processor`
- **Description**: Controls whether the bot will handle trade processing directly (`true`) or rely on another mechanism (`false`).
- **Example**: `false`

## Trade Management

Settings that control how the bot manages open trades.

### `trailing_stop`
- **Description**: Enables or disables trailing stop functionality.
- **Example**: `false` (currently disabled).

### `partial_close`
- **Description**: Allows the bot to close part of a position once it reaches a certain profit level.
- **Example**: `false` (currently disabled).

## Tradable Symbols

This section defines the financial instruments (symbols) the bot is allowed to trade, along with their respective strategies.

### `tradable_symbols`
- **Description**: A dictionary of symbols and their associated strategies.
- **Example**:
  ```json
  {
    "XAUUSD": [
      {
        "granularity": "M1",
        "indicators": {},
        "risk": 0.01,
        "profit_ratio": 1
      }
    ]
  }
  ```

### Symbol Definitions

#### `granularity`
- **Description**: The timeframe for analyzing market data.
- **Example**: `"M1"` (1-minute chart).

#### `indicators`
- **Description**: A dictionary of indicators the bot will use for decision-making.
- **Example**: `{}` (currently empty, but can be populated with specific indicators like moving averages, RSI, etc.).

#### `risk`
- **Description**: The percentage of the account balance to risk on trades for this symbol.
- **Example**: `0.01` (1% risk).

#### `profit_ratio`
- **Description**: The reward-to-risk ratio for trades on this symbol.
- **Example**: `1` (a 1:1 reward-to-risk ratio).

## Usage

To run the bot, make sure to configure all relevant fields in the `configuration.json` file. Here are some steps to start:

1. **Configure Environment Variables**: 
   You can store sensitive information like account credentials in environment variables.
   ```bash
   export ACCOUNT_ID=your_account_id
   export ACCOUNT_PASSWORD=your_account_password
   export ACCOUNT_SERVER=your_broker_server
   ```

2. **Update Configuration**: 
   Edit the `./bot/configuration.json` file to reflect your trading strategy, risk management, and other settings.

3. **Run the Bot**:
   Once configured, run the bot using the appropriate Python command.
   ```bash
   python main.py
   ```

## Important Notes

- Ensure that your environment variables and configurations are correct before running the bot, especially when trading with live funds.
- Adjust risk management settings carefully to suit your risk tolerance.
- Monitor the bot's logs for errors or any unusual behavior.
- Always backtest and forward-test your strategies before deploying the bot on a live account.
