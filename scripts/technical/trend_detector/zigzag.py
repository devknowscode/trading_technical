import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

from ._abstract import __TrendDetector

class ZigZag(__TrendDetector):
    def __init__(self, data: pd.DataFrame, threshold=5.0, depth=10):
        super().__init__(data, threshold)
        self.__depth = depth

    @property
    def depth(self):
        return self.__depth
    
    def find_pivots(self, close, high, low):
        pivots = []
        # find peaks
        peak_indices = argrelextrema(high, np.greater_equal, order=self.depth)[0]
        pivots.extend([pivot for pivot in zip(peak_indices, high[peak_indices], ["High"] * len(peak_indices))])
        # find valleys
        valley_indices = argrelextrema(low, np.less_equal, order=self.depth)[0]
        pivots.extend([pivot for pivot in zip(valley_indices, low[valley_indices], ["Low"] * len(valley_indices))])
        return sorted(pivots)
        

    def fit(self):
        close = self.data["Close"].to_numpy()
        high = self.data["High"].to_numpy()
        low = self.data["Low"].to_numpy()
        # Find pivots
        detected_pivots = self.find_pivots(close, high, low)
        if not detected_pivots:
            return []

        # Assume the first pivot is always one of zigzag points
        zigzag_points = [detected_pivots[0]]
        for i in range(1, len(detected_pivots)):
            last_pivot = zigzag_points[-1]
            current_pivot = detected_pivots[i]

            if current_pivot[2] != last_pivot[2]:
                price_change = abs(current_pivot[1] - last_pivot[1]) / last_pivot[1]
                
                if price_change >= self.threshold:
                    zigzag_points.append(current_pivot)

            else:
                if (len(zigzag_points) > 2):
                    second_last_pivot = zigzag_points[-2]
                    price_change_new = abs(current_pivot[1] - second_last_pivot[1]) / second_last_pivot[1]
                    price_change_prev = abs(last_pivot[1] - second_last_pivot[1]) / second_last_pivot[1]
                    if price_change_new >= price_change_prev:
                        if current_pivot[2] == "High" and current_pivot[1] >= last_pivot[1]:
                            zigzag_points[-1] = current_pivot
                        elif current_pivot[2] == "Low" and current_pivot[1] <= last_pivot[1]:
                            zigzag_points[-1] = current_pivot

        self.pivots = [(self.data.index[i], price, label) for i, price, label in zigzag_points]
        return self.pivots

    def plot(self):
        super().plot()
        plt.title("Zigzag Algorithm")
        plt.show()
