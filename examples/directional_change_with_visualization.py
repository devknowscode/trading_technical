import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.directional_change import DirectionalChange

symbol = "btcusdt"
timeframe = "1d"
# read data
df = pd.read_csv(f"./data/{symbol}{timeframe}.csv".lower(), index_col=["Date"], parse_dates=["Date"])

# zigzag
dc = DirectionalChange(threshold=10.0)
dc.fit(df)
dc.plot(df)
