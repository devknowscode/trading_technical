import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.zigzag import ZigZag

symbol = "btcusdt"
timeframe = "1d"
# read data
df = pd.read_csv(f"./data/{symbol}{timeframe}.csv".lower(), index_col=["Date"], parse_dates=["Date"])

# zigzag
zz = ZigZag(depth=70)
zz.fit(df)
zz.plot(df)