import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pandas as pd
from scripts.volume_profile import VolumeProfile

symbol = "btcusdt"
timeframe = "1d"
# read data
df = pd.read_csv(f"./data/{symbol}{timeframe}.csv".lower(), index_col=["Date"], parse_dates=["Date"])

vp = VolumeProfile(df)
vp.fit()
print(vp.poc)
print(vp.va)
print(vp.profile)

vp.plot()