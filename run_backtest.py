# /rsi_strategy_tsla/run_backtest.py

import config
from src import data_handler, strategy, backtester, plotting
import pprint

def main():
    """
    Main function to run the backtest workflow.
    """
    # 1. Load all configurations into a dictionary
    config_dict = {k: v for k, v in vars(config).items() if not k.startswith('__')}
    
    # 2. Fetch and prepare data
    market_data = data_handler.fetch_and_prepare_data(config_dict)
    
    if market_data.empty:
        print("Exiting due to data loading failure.")
        return

    # 3. Initialize strategy and generate signals
    rsi_strategy = strategy.RsiStrategy(config_dict)
    data_with_signals = rsi_strategy.generate_signals(market_data)

    # 4. Run backtest simulation
    bt = backtester.Backtester(config_dict)
    performance_df, metrics = bt.run(data_with_signals)

    # 5. Print performance metrics
    print("\n--- Backtest Performance Metrics ---")
    pprint.pprint(metrics)
    print("------------------------------------\n")

    # 6. Generate and display plots
    plotting.generate_plots(performance_df, data_with_signals, metrics, config_dict)

if __name__ == "__main__":
    main()