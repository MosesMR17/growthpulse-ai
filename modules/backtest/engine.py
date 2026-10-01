import pandas as pd
import numpy as np

def run_momentum_backtest(price_series, lookback_window=20):
    """
    Simulates a basic time-series momentum strategy:
    - Go long if the past N-day return is positive.
    - Calculate strategy equity curve versus buy-and-hold.
    """
    df = pd.DataFrame(index=price_series.index)
    df['Price'] = price_series
    df['Returns'] = df['Price'].pct_change()
    
    # Momentum signal: N-day lookback return
    df['Signal'] = np.where(df['Price'].pct_change(lookback_window) > 0, 1, 0)
    df['Strategy_Returns'] = df['Signal'].shift(1) * df['Returns']
    
    # Cumulative performance
    df['Buy_Hold_Cum'] = (1 + df['Returns'].fillna(0)).cumprod()
    df['Strategy_Cum'] = (1 + df['Strategy_Returns'].fillna(0)).cumprod()
    
    return df[['Price', 'Buy_Hold_Cum', 'Strategy_Cum', 'Signal']]
