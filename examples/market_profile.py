import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from scripts.technical.profile_analyzer import MarketProfile

symbol = "btcusdt"
timeframe = "1d"
# read data
df = pd.read_csv(
    f"./data/{symbol}{timeframe}.csv".lower(), index_col=["Date"], parse_dates=["Date"]
)

mp = MarketProfile(df)
mp.fit()
print(mp.poc)
print(mp.va)
print(mp.profile)

mp.plot()
