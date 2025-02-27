import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from ._abstract import Profile

class MarketProfile(Profile):
    def __init__(self, data = None, bin_size=100, perc=70):
        super().__init__(data, bin_size, perc)
    
    def fit(self):
        if self.data is None:
            raise ValueError("Error: `data` is required but missing")
        
        price_min = self.data["Low"].min()
        price_max = self.data["High"].max()
        bins, bin_step = np.linspace(price_min, price_max, self.bin_size, retstep=True)
        tpo_counts = np.zeros(len(bins))
        
        for _, row in self.data.iterrows():
            price_range = np.arange(row["Low"], row["High"], bin_step)
            indicies = np.digitize(price_range, bins)
            for idx in indicies:
                if 0 <= idx < len(tpo_counts):
                    tpo_counts[idx] += 1
                
        profile = pd.DataFrame({
            "Price": np.round(bins, 2),
            "TPOs": tpo_counts
        })
        profile = profile.sort_values(by="Price", ascending=False)
        
        self.profile = profile
        self.poc = self.poc()
        self.va = self.value_area()

    def poc(self):
        poc_idx = np.argmax(self.profile["TPOs"])
        poc = self.profile.iloc[poc_idx]["Price"]
        
        return [poc_idx, poc]

    def value_area(self):
        total_tpos = self.profile["TPOs"].sum()
        va = total_tpos * self.perc / 100
        
        cumulative_tpos = 0
        value_prices = []
        profile = self.profile.sort_values(by="TPOs", ascending=False)
        
        for _, row in profile.iterrows():
            value_prices.append(row["Price"])
            cumulative_tpos += row["TPOs"]
            if cumulative_tpos > va:
                break
            
        return (min(value_prices), max(value_prices))
    
    def plot(self):
        # Create figure and axes
        fig, axes = plt.subplots(1, 2, figsize=(20, 8), gridspec_kw={"width_ratios": [3, 1]}, facecolor="black", sharey=True)
        fig.subplots_adjust(wspace=0)

        # ** LEFT CHART: Price time series **
        axes[0].plot(self.data.index, self.data["Close"], color="#FFB22C", linewidth=1)
        axes[0].axhline(self.poc[1], color="#fff", linestyle="-", linewidth=1, label="POC")
        # axes[0].hlines(price_levels, xmin=self.data.index.min(), xmax=self.data.index.max(), color="#854836", linestyle="dashed", linewidth=1)
        # axes[0].scatter(nearest_points, self.data["Close"].loc[nearest_points], color="#F2F6D0", s=30)
        axes[0].set_facecolor("black")
        axes[0].tick_params(axis="x", colors="white")
        axes[0].tick_params(axis="y", colors="white")
        axes[0].set_title("Bitcoin Price Chart", fontweight="bold", color="#FFB22C")
        axes[0].grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)

        axes[0].margins(0)
        axes[0].set_xlim(self.data.index.min(), self.data.index.max())

        # **RIGHT CHART: Market Profile (Price Distribution)**
        alphas = (np.where((self.profile["Price"] >= self.va[0]) & (self.profile["Price"] <= self.va[1]), 1, 0.5))
        rbga = np.zeros((len(self.profile), 4))
        # convert hex to rbg: #ffb22c ---> (255, 178, 44) ---> (1, 0.7, 0.17) --- (num of rgb / 255)
        rbga[:, 0] = 1
        rbga[:, 1] = 0.7
        rbga[:, 2] = 0.17
        rbga[:, 3] = alphas
        
        # Plot to chart
        axes[1].barh(self.profile["Price"][:-1], self.profile["TPOs"][:-1], height=np.diff(self.profile["Price"]), orientation="horizontal", color=rbga, edgecolor="black")
        axes[1].axhline(self.poc[1], color="#fff", linestyle="-", linewidth=1, label="POC")
        
        # Add label of profile
        axes[1].text(0, self.poc[1] * 0.995, "◀ POC", fontsize=8, fontweight="bold", color="white")
        axes[1].text(0, self.va[0] * 0.995, "◀ VAL", fontsize=8, fontweight="bold", color="white")
        axes[1].text(0, self.va[1] * 0.995, "◀ VAH", fontsize=8, fontweight="bold", color="white")
        
        # kde
        # axes[1].plot(self.pdf * sigma, price_range, color="#F2F6D0", linestyle="--", linewidth=1.5)
        # axes[1].scatter(self.pdf[peaks] * sigma, price_levels, color="#F2F6D0", s=50, marker='x')
        axes[1].set_facecolor("black")
        axes[1].tick_params(axis="x", colors="white")
        axes[1].yaxis.tick_right()
        axes[1].set_title("Market Profile", fontweight="bold", color="#FFB22C")
        axes[1].invert_xaxis()
        axes[1].grid(True, linestyle="--", linewidth=0.5, color="#F2F6D0", alpha=0.5)

        # Show plot
        plt.show()
