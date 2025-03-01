import pandas as pd
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.ta.trend_detector.zigzag import ZigZag

symbol = "btcusdt"
timeframe = "1d"
# read data
df = pd.read_csv(f"./data/{symbol}{timeframe}.csv".lower(), index_col=["Date"], parse_dates=["Date"])

# zigzag
zz = ZigZag()
zz.fit(df)
print(zz.pivots)

