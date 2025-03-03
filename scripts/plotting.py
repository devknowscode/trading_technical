import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "")))

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta
from pathlib import Path

import technical.profile_analyzer as Profiler
from utils.downloader import downloader
from utils.ccxt_helpers import timeframe_to_seconds


class Plotting:
    def __init__(
        self, symbol: str, timeframe: str = "5m", limit: int = 1000, interval: int = 1
    ):
        """
        Initializes the live plotter for Market Profile.

        Params:
        - symbol: Trading pair (e.g., "BTCUSDT").
        - timeframe: Timeframe (e.g., "1h").
        - limit: Number of candles to fetch.
        - interval: Update interval in seconds.
        """
        self.symbol = symbol
        self.timeframe = timeframe
        self.limit = limit
        self.interval = interval
        self.data_path = Path(f"./data/{symbol.lower()}{timeframe}.csv")

        # Create figure and axes
        self.fig, self.axes = plt.subplots(
            1,
            2,
            figsize=(20, 8),
            gridspec_kw={"width_ratios": [3, 1]},
            facecolor="black",
            sharey=True,
        )
        self.fig.subplots_adjust(wspace=0.05)

        # Initialize plot elements
        (self.price_line,) = self.axes[0].plot([], [], color="#FFB22C", linewidth=1)
        self.poc_line_0 = self.axes[0].axhline(
            0, color="white", linestyle="-", linewidth=1.5
        )
        self.poc_line_1 = self.axes[1].axhline(
            0, color="white", linestyle="-", linewidth=1.5
        )
        self.profile_bars = None  # Market Profile bars

        self.texts = {}  # Dictionary to hold text labels

        # Configure Axes
        for ax in self.axes:
            ax.set_facecolor("black")
            ax.tick_params(axis="x", colors="white")
            ax.tick_params(axis="y", colors="white")
            ax.grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)

        self.axes[0].set_title(
            f"Bitcoin Price Chart - {self.timeframe}",
            fontweight="bold",
            color="#FFB22C",
        )
        self.axes[1].invert_xaxis()
        self.axes[1].yaxis.tick_right()

    def load_data(self, start: str, end: str | None, exchange_id: str):
        """Loads data from a local file or downloads it if missing."""

        def download_data(start, end=None):
            """Helper function to download missing data."""
            return downloader(
                exchange_id=exchange_id,
                symbol=self.symbol,
                start=start.isoformat(),
                end=end.isoformat() if end else None,
                timeframe=self.timeframe,
            )

        since, until = datetime.fromisoformat(start), (
            datetime.fromisoformat(end) if end else None
        )

        if not self.data_path.exists():
            return download_data(start=since, end=until)
        else:
            data = pd.read_csv(self.data_path, index_col=["Date"], parse_dates=["Date"])
            data_start, data_end = data.index[0], data.index[-1]

            if since in data.index and (until in data.index if until else True):
                data = data.loc[start:end]

            # Determine appropriate download range
            since = min(data_start, since) if since <= data_end else data_end
            until = max(until, data_end) if until else None
            return download_data(start=since, end=until)

    def plot(
        self,
        start: str,
        end: str | None = None,
        exchange_id: str = "binance",
        profile_type: str = "MarketProfile",
    ):
        """Plot market/volume profile based on historical price data."""
        data = self.load_data(start, end, exchange_id)
        profile, poc, value_area = getattr(Profiler, profile_type)(data).fit()

        # ** LEFT CHART: Price time series **
        self.price_line.set_data(data.index, data["Close"])
        self.poc_line_0.set_ydata([poc[1]])

        self.axes[0].set_xlim(data.index.min(), data.index.max())
        self.axes[0].set_ylim(data["Low"].min(), data["High"].max())

        # **RIGHT CHART: Market Profile (Price Distribution)**
        alphas = np.where(
            (profile["Price"] >= value_area[0]) & (profile["Price"] <= value_area[1]),
            1,
            0.5,
        )
        # convert hex to rbg: #ffb22c ---> (255, 178, 44) ---> (1, 0.7, 0.17) --- (num of rgb / 255)
        colors = np.row_stack([[1, 0.7, 0.17, a] for a in alphas])

        # Plot to chart
        self.profile_bars = self.axes[1].barh(
            profile["Price"][:-1],
            (
                profile["TPOs"][:-1]
                if profile_type == "MarketProfile"
                else profile["Volume"][:-1]
            ),
            orientation="horizontal",
            height=np.diff(profile["Price"]),
            color=colors,
            edgecolor="black",
        )
        self.poc_line_1.set_ydata([poc[1]])

        # Update text labels
        label_positions = {"POC": poc[1], "VAL": value_area[0], "VAH": value_area[1]}
        for label, y in label_positions.items():
            if label not in self.texts:
                self.texts[label] = self.axes[1].text(
                    0, y, f"◀ {label}", fontsize=8, fontweight="bold", color="white"
                )
            else:
                self.texts[label].set_position((0, y))

        # kde
        # axes[1].plot(self.pdf * sigma, price_range, color="#F2F6D0", linestyle="--", linewidth=1.5)
        # axes[1].scatter(self.pdf[peaks] * sigma, price_levels, color="#F2F6D0", s=50, marker='x')
        self.axes[1].set_title(
            "Market Profile" if profile_type == "MarketProfile" else "Volume Profile",
            fontweight="bold",
            color="#FFB22C",
        )

        # Show plot
        plt.show()

    def update(self, frame, exchange_id: str, profile_type: str):
        # set start date to download data
        since = None
        if self.data_path.exists():
            data_csv = pd.read_csv(
                self.data_path, index_col=["Date"], parse_dates=["Date"]
            )
            since = data_csv.index[-1].isoformat()
        else:
            since = (
                datetime.now()
                - timedelta(seconds=(timeframe_to_seconds(self.timeframe) * 86400))
            ).isoformat()

        downloader(
            exchange_id=exchange_id,
            symbol=self.symbol,
            start=since,
            timeframe=self.timeframe,
        )

        # Read only the last 100 rows instead of the entire file
        data = pd.read_csv(self.data_path, index_col=["Date"], parse_dates=["Date"])
        data = data[-100:]

        # Compute profile
        profile, poc, value_area = getattr(Profiler, profile_type)(data).fit()

        # ** Update Price Chart **
        self.price_line.set_data(data.index, data["Close"])
        self.poc_line_0.set_ydata([poc[1]])

        self.axes[0].set_xlim(data.index.min(), data.index.max())
        self.axes[0].set_ylim(data["Low"].min(), data["High"].max())

        # ** Update Profiler Chart **
        alphas = np.where(
            (profile["Price"] >= value_area[0]) & (profile["Price"] <= value_area[1]),
            1,
            0.3,
        )
        colors = np.row_stack([[1, 0.7, 0.17, a] for a in alphas])

        # Remove old bars before plotting new ones
        if self.profile_bars is not None:
            for bar in self.profile_bars:
                bar.remove()

        # Plot bar chart
        self.profile_bars = self.axes[1].barh(
            profile["Price"][:-1],
            (
                profile["TPOs"][:-1]
                if profile_type == "MarketProfile"
                else profile["Volume"][:-1]
            ),
            orientation="horizontal",
            height=np.diff(profile["Price"]),
            color=colors,
            edgecolor="black",
        )

        self.poc_line_1.set_ydata([poc[1]])

        # Update text labels
        label_positions = {"POC": poc[1], "VAL": value_area[0], "VAH": value_area[1]}
        for label, y in label_positions.items():
            if label not in self.texts:
                self.texts[label] = self.axes[1].text(
                    0, y, f"◀ {label}", fontsize=8, fontweight="bold", color="white"
                )
            else:
                self.texts[label].set_position((0, y))

        self.axes[1].set_title(
            "Market Profile" if profile_type == "MarketProfile" else "Volume Profile",
            fontweight="bold",
            color="#FFB22C",
        )

        self.fig.canvas.draw_idle()

    def live(self, exchange_id: str = "binance", profile_type: str = "MarketProfile"):
        anim = FuncAnimation(
            self.fig,
            self.update,
            interval=self.interval * 1000,
            cache_frame_data=False,
            fargs=(
                exchange_id,
                profile_type,
            ),
        )
        plt.show()
