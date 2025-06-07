# /rsi_strategy_tsla/src/plotting.py

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from typing import Dict, Any

def generate_plots(
    performance_df: pd.DataFrame, 
    data_with_signals: pd.DataFrame, 
    metrics: Dict[str, float],
    config: Dict[str, Any]
):
    """
    Generates and displays performance charts for the backtest.
    """
    print("Generating plots...")
    plt.style.use('seaborn-v0_8-darkgrid')
    
    # --- Plot 1: Equity Curve vs. Buy & Hold ---
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1]})
    fig.suptitle(f"Backtest Results for {config['TICKER']} ({config['TIME_FRAME']} RSI Strategy)", fontsize=16)

    # Equity Curve
    ax1.plot(performance_df.index, performance_df['total_value'], label='Strategy Equity', color='blue', lw=2)
    
    # Buy & Hold Benchmark
    buy_hold_equity = (data_with_signals['Close'] / data_with_signals['Close'].iloc[0]) * config['INITIAL_CAPITAL']
    ax1.plot(buy_hold_equity.index, buy_hold_equity, label='Buy & Hold Equity', color='grey', linestyle='--', lw=2)
    
    ax1.set_ylabel('Portfolio Value ($)')
    ax1.set_title('Equity Curve')
    ax1.legend()
    ax1.ticklabel_format(style='plain', axis='y') # No scientific notation

    # Drawdown Plot
    running_max = performance_df['total_value'].cummax()
    drawdown = (performance_df['total_value'] - running_max) / running_max
    ax2.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
    ax2.plot(drawdown.index, drawdown, color='red', lw=1)
    ax2.set_ylabel('Drawdown (%)')
    ax2.set_title('Portfolio Drawdown')
    ax2.yaxis.set_major_formatter(plt.FuncFormatter('{:.0%}'.format))
    ax2.set_xlabel('Date')
    
    # Format x-axis
    fig.autofmt_xdate()
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.tight_layout(rect=[0, 0.03, 1, 0.96]) # Adjust for suptitle
    plt.show()

    # --- Plot 2: Price with RSI and Trade Signals ---
    fig2, (ax3, ax4) = plt.subplots(2, 1, figsize=(14, 10), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
    
    # Price and Trade Markers
    ax3.plot(data_with_signals.index, data_with_signals['Close'], label='Close Price', color='black')
    
    buy_signals = data_with_signals[data_with_signals['signal'] == 1]
    sell_signals = data_with_signals[data_with_signals['signal'] == -1]
    
    ax3.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='green', s=100, label='Buy Signal', zorder=5)
    ax3.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='red', s=100, label='Sell Signal', zorder=5)
    
    ax3.set_ylabel('Price ($)')
    ax3.set_title(f"{config['TICKER']} Price and Trade Signals")
    ax3.legend()

    # RSI Plot
    ax4.plot(data_with_signals.index, data_with_signals['rsi'], label='RSI', color='purple')
    ax4.axhline(config['RSI_THRESHOLD'], color='gray', linestyle='--', label=f'Threshold ({config["RSI_THRESHOLD"]})')
    ax4.set_ylabel('RSI Value')
    ax4.set_title(f"{config['RSI_PERIOD']}-Period RSI")
    ax4.set_xlabel('Date')
    ax4.legend()

    # Format x-axis
    fig2.autofmt_xdate()
    ax4.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    plt.tight_layout()
    plt.show()