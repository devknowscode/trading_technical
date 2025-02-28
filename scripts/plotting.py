import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from .utils.downloader import downloader
from .market_profile import MarketProfile

class Plotting():
    def __init__(self, symbol="BTCUSDT", timeframe="1h", limit=1000, interval=1000):
        """
        Initializes the live plotter for Market Profile.

        Params:
        - symbol: Trading pair (e.g., "BTCUSDT").
        - timeframe: Timeframe (e.g., "1h").
        - limit: Number of candles to fetch.
        - interval: Update interval in milliseconds.
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.interval = interval

        # Create figure and axes
        self.fig, self.axes = plt.subplots(1, 2, figsize=(20, 8), gridspec_kw={"width_ratios": [3, 1]}, facecolor="black", sharey=True)
        self.fig.subplots_adjust(wspace=0.1)
        
        # Initialize plot elements
        self.price_line, = self.axes[0].plot([], [], color="#FFB22C", linewidth=1)
        self.poc_line_0 = self.axes[0].axhline(0, color="white", linestyle="-", linewidth=1)
        self.poc_line_1 = self.axes[1].axhline(0, color="white", linestyle="-", linewidth=1)
        self.profile_bars = None  # Market Profile bars

        self.texts = {}  # Dictionary to hold text labels
        
        # axes[0]
        self.axes[0].set_facecolor("black")
        self.axes[0].tick_params(axis="x", colors="white")
        self.axes[0].tick_params(axis="y", colors="white")
        self.axes[0].set_title("Bitcoin Price Chart", fontweight="bold", color="#FFB22C")
        self.axes[0].grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)

        self.axes[0].margins(0)
        
        # axes[1]
        self.axes[1].set_facecolor("black")
        self.axes[1].tick_params(axis="x", colors="white")
        self.axes[1].yaxis.tick_right()
        self.axes[1].invert_xaxis()
        self.axes[1].set_title("Market Profile", fontweight="bold", color="#FFB22C")
        self.axes[1].grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)


    def plot(self):
        data = downloader("binance", "BTCUSDT", "1h", 1000)
        profile, poc, value_area = MarketProfile(data).fit()
        
        # Create figure and axes
        self.fig.subplots_adjust(wspace=0)

        # ** LEFT CHART: Price time series **
        self.axes[0].plot(data.index, data["Close"], color="#FFB22C", linewidth=1)
        self.axes[0].axhline(poc[1], color="#fff", linestyle="-", linewidth=1, label="POC")
        self.axes[0].set_facecolor("black")
        self.axes[0].tick_params(axis="x", colors="white")
        self.axes[0].tick_params(axis="y", colors="white")
        self.axes[0].set_title("Bitcoin Price Chart", fontweight="bold", color="#FFB22C")
        self.axes[0].grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)

        self.axes[0].margins(0)
        self.axes[0].set_xlim(data.index.min(), data.index.max())

        # **RIGHT CHART: Market Profile (Price Distribution)**
        alphas = (np.where((profile["Price"] >= value_area[0]) & (profile["Price"] <= value_area[1]), 1, 0.5))
        rbga = np.zeros((len(profile), 4))
        # convert hex to rbg: #ffb22c ---> (255, 178, 44) ---> (1, 0.7, 0.17) --- (num of rgb / 255)
        rbga[:, 0] = 1
        rbga[:, 1] = 0.7
        rbga[:, 2] = 0.17
        rbga[:, 3] = alphas
        
        # Plot to chart
        self.axes[1].barh(profile["Price"][:-1], profile["TPOs"][:-1], height=np.diff(profile["Price"]), orientation="horizontal", color=rbga, edgecolor="black")
        self.axes[1].axhline(poc[1], color="#fff", linestyle="-", linewidth=1, label="POC")
        
        # Add label of profile
        self.axes[1].text(0, poc[1], "◀ POC", fontsize=8, fontweight="bold", color="white")
        self.axes[1].text(0, value_area[0], "◀ VAL", fontsize=8, fontweight="bold", color="white")
        self.axes[1].text(0, value_area[1], "◀ VAH", fontsize=8, fontweight="bold", color="white")
        
        # kde
        # axes[1].plot(self.pdf * sigma, price_range, color="#F2F6D0", linestyle="--", linewidth=1.5)
        # axes[1].scatter(self.pdf[peaks] * sigma, price_levels, color="#F2F6D0", s=50, marker='x')
        self.axes[1].set_facecolor("black")
        self.axes[1].tick_params(axis="x", colors="white")
        self.axes[1].yaxis.tick_right()
        self.axes[1].set_title("Market Profile", fontweight="bold", color="#FFB22C")
        self.axes[1].invert_xaxis()
        self.axes[1].grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)

        # Show plot
        plt.show()

    
    def update(self, frame):
        data = downloader("binance", self.symbol, self.timeframe, self.limit)
        profile, poc, value_area = MarketProfile(data).fit()

        # ** LEFT CHART: Price time series **
        self.price_line.set_data(data.index, data["Close"])
        self.poc_line_0.set_ydata([poc[1]])
        
        self.axes[0].set_xlim(data.index.min(), data.index.max())
        self.axes[0].set_ylim(data["Low"].min(), data["High"].max())

        # **RIGHT CHART: Market Profile (Price Distribution)**
        alphas = (np.where((profile["Price"] >= value_area[0]) & (profile["Price"] <= value_area[1]), 1, 0.3))
        colors = np.row_stack([[1, 0.7, 0.17, a] for a in alphas])
        
        # Plot to chart
        self.profile_bars = self.axes[1].barh(profile["Price"][:-1], profile["TPOs"][:-1],
                                                orientation="horizontal",
                                                height=np.diff(profile["Price"]),
                                                color=colors, edgecolor="black")
        
        self.poc_line_1.set_ydata([poc[1]])
        
        # Update text labels
        label_positions = {"POC": poc[1], "VAL": value_area[0], "VAH": value_area[1]}
        for label, y in label_positions.items():
            if label not in self.texts:
                self.texts[label] = self.axes[1].text(0, y, f"◀ {label}", fontsize=8, fontweight="bold", color="white")
            else:
                self.texts[label].set_position((0, y))
    
    def live(self):
        ani = FuncAnimation(self.fig, self.update, interval=self.interval, cache_frame_data=False)
        plt.show()
