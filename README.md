# 3-Day RSI Strategy with Advanced Trade Management

This repository contains a professional-grade Python backtesting engine to test an RSI-based trading strategy on Tesla (TSLA) stock, featuring active trade management with partial take-profits and a breakeven stop-loss.

## Strategy Logic

-   **Asset**: Tesla Inc. (TSLA)
-   **Timeframe**: 3-Day (3D) bars, resampled from daily data.
-   **Entry Signal**: A "BUY" signal is generated when the 30-period RSI crosses **above** 50.
-   **Trade Management**:
    -   **Breakeven Stop-Loss**: After the position gains 10%, a stop-loss is placed at the entry price.
    -   **Partial Take-Profits**:
        -   At +30% gain, sell 30% of the initial position.
        -   At +70% gain, sell 30% of the initial position.
        -   At +120% gain, sell 30% of the initial position.
-   **Final Exit Signal**: The remainder of the position is sold when the RSI crosses **below** 50.

## How to Run

1.  **Clone & Setup**:
    ```bash
    git clone https://github.com/[Your-GitHub-Username]/rsi_strategy_tsla.git
    cd rsi_strategy_tsla
    pip install -r requirements.txt
    ```
2.  **Run**:
    ```bash
    python run_backtest.py
    ```
The script will run the full backtest, print a detailed log of every trade action (entry, take-profit, stop-loss, exit), display a final performance report, and show performance charts.