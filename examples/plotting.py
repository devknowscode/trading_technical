import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.plotting import Plotting
from scripts.utils.ccxt_helpers import timeframe_to_seconds

symbol = "BTCUSDT"
timeframe = "1m"

plotter = Plotting(
    symbol=symbol, timeframe=timeframe, interval=timeframe_to_seconds(timeframe)
)  # seconds
# plotter.plot(start="2024-01-01", end="2024-01-02", profile_type="MarketProfile")
plotter.live(profile_type="VolumeProfile")
