# /rsi_strategy_tsla/config.py

from datetime import datetime, timedelta

# --- DATA CONFIGURATION ---
TICKER: str = "TSLA"
START_DATE: str = (datetime.now() - timedelta(days=6*365)).strftime('%Y-%m-%d')
END_DATE: str = datetime.now().strftime('%Y-%m-%d')

# --- STRATEGY CONFIGURATION ---
TIME_FRAME: str = "3D"
RSI_PERIOD: int = 30
RSI_THRESHOLD: int = 50

# --- BACKTEST & TRADE MANAGEMENT CONFIGURATION ---
INITIAL_CAPITAL: float = 100_000.0

# --- NEW: Define the take-profit and stop-loss rules ---
# Breakeven Rule
BREAKEVEN_TRIGGER_PCT: float = 0.10  # 10% gain to trigger breakeven stop

# Partial Take-Profit Rules
# A list of rules. Each rule is a dictionary.
# 'gain_pct': The profit % that triggers the sale.
# 'size_pct': The % of the *initial* position to sell.
PARTIAL_EXIT_RULES = [
    {'gain_pct': 0.30, 'size_pct': 0.30},  # At 30% gain, sell 30% of initial position
    {'gain_pct': 0.70, 'size_pct': 0.30},  # At 70% gain, sell 30% of initial position
    {'gain_pct': 1.20, 'size_pct': 0.30},  # At 120% gain, sell 30% of initial position
]