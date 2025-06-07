# /rsi_strategy_tsla/src/strategy.py

import pandas as pd
import pandas_ta as ta
from typing import Dict, Any

class RsiStrategy:
    """
    Encapsulates the RSI trading strategy logic for generating signals.
    """
    def __init__(self, config: Dict[str, Any]):
        """
        Initializes the RsiStrategy with given configuration.

        Args:
            config (Dict[str, Any]): Configuration dictionary with strategy parameters.
        """
        self.rsi_period = config['RSI_PERIOD']
        self.rsi_threshold = config['RSI_THRESHOLD']

    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generates buy and sell signals based on the RSI indicator.

        Args:
            data (pd.DataFrame): The input market data with OHLCV columns.

        Returns:
            pd.DataFrame: The data DataFrame augmented with 'rsi' and 'signal' columns.
        """
        if data.empty:
            return data

        print("Generating trading signals...")
        
        # Calculate RSI
        data['rsi'] = ta.rsi(data['Close'], length=self.rsi_period)
        data.dropna(inplace=True) # Drop rows where RSI could not be calculated

        # --- Generate Raw Crossover Signals ---
        # A buy signal is when RSI crosses ABOVE the threshold
        # A sell signal is when RSI crosses BELOW the threshold
        data['crossover'] = 0
        
        # Previous RSI values
        prev_rsi = data['rsi'].shift(1)
        
        # Condition for crossing up
        is_crossing_up = (prev_rsi < self.rsi_threshold) & (data['rsi'] >= self.rsi_threshold)
        
        # Condition for crossing down
        is_crossing_down = (prev_rsi > self.rsi_threshold) & (data['rsi'] <= self.rsi_threshold)

        data.loc[is_crossing_up, 'crossover'] = 1  # Raw Buy Signal
        data.loc[is_crossing_down, 'crossover'] = -1 # Raw Sell Signal

        # --- Filter signals to ensure they alternate ---
        # We can't buy if we are already in a position, and can't sell if we are not.
        position = 0  # 0 = out of market, 1 = in market
        signals = []
        for index, row in data.iterrows():
            if position == 0 and row['crossover'] == 1:
                signals.append(1)  # Buy
                position = 1
            elif position == 1 and row['crossover'] == -1:
                signals.append(-1) # Sell
                position = 0
            else:
                signals.append(0)  # Hold
        
        data['signal'] = signals
        
        print("Signals generated.")
        return data