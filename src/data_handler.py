# /rsi_strategy_tsla/src/data_handler.py

import pandas as pd
import yfinance as yf
from typing import Dict, Any

def fetch_and_prepare_data(config: Dict[str, Any]) -> pd.DataFrame:
    """
    Fetches daily stock data and resamples it to the specified timeframe.
    """
    print(f"Fetching data for {config['TICKER']} from {config['START_DATE']} to {config['END_DATE']}...")

    try:
        # Fetch daily data
        daily_data = yf.download(
            config['TICKER'],
            start=config['START_DATE'],
            end=config['END_DATE'],
            progress=False,
            auto_adjust=False,
            actions=False
        )

        if daily_data.empty:
            print(f"No data found for {config['TICKER']}. Please check the ticker and date range.")
            return pd.DataFrame()

        # --- THE FINAL, CORRECT FIX ---
        # If the columns are a MultiIndex, select the first level ('Open', 'Close', etc.)
        # and assign it as the new, simple column index.
        if isinstance(daily_data.columns, pd.MultiIndex):
            daily_data.columns = daily_data.columns.get_level_values(0)

        # Define the aggregation logic
        aggregation_rules = {
            'Open': 'first',
            'High': 'max',
            'Low': 'min',
            'Close': 'last',
            'Volume': 'sum'
        }

        # Resample to the desired timeframe
        resampled_data = daily_data.resample(config['TIME_FRAME']).apply(aggregation_rules)

        # Drop any rows with NaN values that result from resampling
        resampled_data.dropna(inplace=True)

        print(f"Data fetched and resampled to {config['TIME_FRAME']} successfully.")
        return resampled_data

    except Exception as e:
        print(f"An error occurred during data fetching: {e}")
        return pd.DataFrame()