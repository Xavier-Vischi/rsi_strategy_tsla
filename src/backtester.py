# /rsi_strategy_tsla/src/backtester.py

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple

class Backtester:
    """
    A stateful, iterative backtester for evaluating trading strategies
    with complex trade management rules like take-profits and stop-losses.
    This version correctly carries over portfolio state day-to-day.
    """
    def __init__(self, config: Dict[str, Any]):
        """Initializes the Backtester with all configuration."""
        self.initial_capital = config['INITIAL_CAPITAL']
        self.breakeven_trigger = config['BREAKEVEN_TRIGGER_PCT']
        # Sort rules by gain percentage to process highest first
        self.partial_exit_rules = sorted(
            config['PARTIAL_EXIT_RULES'], 
            key=lambda x: x['gain_pct'], 
            reverse=True
        )

    def run(self, data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, float]]:
        """Runs the backtest simulation with active trade management."""
        print("Running advanced backtest simulation with take-profits...")
        
        # --- Portfolio Initialization ---
        portfolio = pd.DataFrame(index=data.index)
        portfolio['holdings'] = 0.0
        portfolio['cash'] = self.initial_capital
        portfolio['total_value'] = self.initial_capital
        portfolio['trades'] = 0

        # --- Trade State Variables ---
        in_position = False
        entry_price = 0.0
        stop_loss_price = 0.0
        initial_position_value = 0.0
        current_shares = 0.0
        tp_triggers_fired = []

        # --- Main Backtest Loop ---
        # We start from the second row to be able to look back at the previous day's state
        for i in range(1, len(data)):
            # Carry over state from the previous day
            portfolio.iloc[i] = portfolio.iloc[i-1]
            current_date = data.index[i]
            
            # Get current day's price data
            current_price = data['Close'].iloc[i]
            high_price = data['High'].iloc[i]
            low_price = data['Low'].iloc[i]
            
            # --- Active Trade Management (if in a position) ---
            if in_position:
                # 1. Check for Stop-Loss
                if low_price <= stop_loss_price:
                    sale_proceeds = current_shares * stop_loss_price
                    portfolio.loc[current_date, 'cash'] += sale_proceeds
                    portfolio.loc[current_date, 'trades'] -= 1
                    print(f"{str(current_date.date())}: STOP-LOSS triggered at ${stop_loss_price:.2f}. Selling {current_shares:.2f} shares.")
                    in_position = False # Reset state
                    current_shares = 0.0
                else:
                    unrealized_gain_pct = (high_price / entry_price) - 1

                    # 2. Check for Breakeven Stop-Loss Activation
                    if unrealized_gain_pct >= self.breakeven_trigger and stop_loss_price < entry_price:
                        stop_loss_price = entry_price
                        print(f"{str(current_date.date())}: Breakeven Stop-Loss activated at ${entry_price:.2f}.")

                    # 3. Check for Take-Profit Triggers
                    for rule in self.partial_exit_rules:
                        level = rule['gain_pct']
                        if unrealized_gain_pct >= level and level not in tp_triggers_fired:
                            shares_to_sell = (initial_position_value * rule['size_pct']) / entry_price
                            shares_to_sell = min(shares_to_sell, current_shares) # Can't sell more than we have
                            
                            if shares_to_sell > 0:
                                execution_price = entry_price * (1 + level)
                                sale_proceeds = shares_to_sell * execution_price
                                portfolio.loc[current_date, 'cash'] += sale_proceeds
                                portfolio.loc[current_date, 'trades'] -= 1
                                current_shares -= shares_to_sell
                                tp_triggers_fired.append(level)
                                print(f"{str(current_date.date())}: TAKE-PROFIT {int(level*100)}% triggered. Selling {shares_to_sell:.2f} shares.")

                    # 4. Check for Final RSI Exit Signal
                    if data['signal'].iloc[i] == -1:
                        if current_shares > 0:
                            sale_proceeds = current_shares * current_price
                            portfolio.loc[current_date, 'cash'] += sale_proceeds
                            portfolio.loc[current_date, 'trades'] -= 1
                            print(f"{str(current_date.date())}: Final RSI SELL signal. Selling remaining {current_shares:.2f} shares.")
                        in_position = False
                        current_shares = 0.0

            # --- Check for New Entry Signal ---
            if not in_position and data['signal'].iloc[i] == 1:
                cash_to_invest = portfolio['cash'].iloc[i]
                entry_price = current_price
                current_shares = cash_to_invest / entry_price
                initial_position_value = cash_to_invest
                
                portfolio.loc[current_date, 'cash'] = 0.0
                portfolio.loc[current_date, 'trades'] += 1
                
                # Reset trade state variables for the new trade
                in_position = True
                stop_loss_price = 0.0 # No stop-loss until breakeven is hit
                tp_triggers_fired = []
                print(f"\n{str(current_date.date())}: NEW TRADE | BUY signal. Buying {current_shares:.2f} shares at ${entry_price:.2f}.")

            # Update portfolio value for the day with the current price
            portfolio.loc[current_date, 'holdings'] = current_shares * current_price
            portfolio.loc[current_date, 'total_value'] = portfolio.loc[current_date, 'cash'] + portfolio.loc[current_date, 'holdings']

        metrics = self._calculate_metrics(portfolio, data)
        print("\nBacktest simulation finished.")
        return portfolio, metrics

    def _calculate_metrics(self, portfolio: pd.DataFrame, data: pd.DataFrame) -> Dict[str, float]:
        """Calculates key performance indicators."""
        print("Calculating performance metrics...")
        
        total_return = (portfolio['total_value'].iloc[-1] / self.initial_capital) - 1
        days_in_backtest = (portfolio.index[-1] - portfolio.index[0]).days
        years_in_backtest = days_in_backtest / 365.25 if days_in_backtest > 0 else 1
        cagr = ((portfolio['total_value'].iloc[-1] / self.initial_capital) ** (1 / years_in_backtest) - 1) if years_in_backtest > 0 else 0

        portfolio['returns'] = portfolio['total_value'].pct_change().fillna(0)
        
        annualization_factor = 252 / 3
        if portfolio['returns'].std() > 0:
            sharpe_ratio = (portfolio['returns'].mean() * annualization_factor) / (portfolio['returns'].std() * np.sqrt(annualization_factor))
        else:
            sharpe_ratio = 0

        running_max = portfolio['total_value'].cummax()
        drawdown = (portfolio['total_value'] - running_max) / running_max
        max_drawdown = drawdown.min()
        
        calmar_ratio = cagr / abs(max_drawdown) if max_drawdown != 0 else np.inf
        
        num_trades = portfolio[portfolio['trades'] > 0].shape[0]
        
        buy_hold_return = (data['Close'].iloc[-1] / data['Close'].iloc[0]) - 1
        
        metrics = {
            "Total Return (%)": total_return * 100,
            "Buy & Hold Return (%)": buy_hold_return * 100,
            "CAGR (%)": cagr * 100,
            "Sharpe Ratio": sharpe_ratio,
            "Max Drawdown (%)": max_drawdown * 100,
            "Calmar Ratio": calmar_ratio,
            "Number of Trades": num_trades
        }
        return metrics