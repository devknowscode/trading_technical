from abc import ABC, abstractmethod
import pandas as pd
import matplotlib.pyplot as plt

class PriceLevels(ABC):
    def __init__(self, data: pd.DataFrame, threshold: float):
        super().__init__()
        self.__data = data
        self.__threshold = threshold / 100
        self.__pivots = []
        
    @property
    def data(self):
        return self.__data

    @property
    def threshold(self):
        return self.__threshold

    @property
    def pivots(self):
        return self.__pivots
    
    @pivots.setter
    def pivots(self, pivots):
        self.__pivots = pivots

    @abstractmethod
    def find_pivots(self, close, high, low):
        pass
    
    @abstractmethod
    def fit(self):
        pass
    
    def plot(self):
        plt.figure(figsize=(20, 6))
        plt.plot(self.data.index, self.data["Close"], label="Price", color="blue", alpha=0.5)
        
        if self.pivots:
            pivot_dates, pivot_prices, pivot_labels = zip(*self.pivots)
            plt.scatter(pivot_dates, pivot_prices, c=["green" if label == "High" else "red" for label in pivot_labels], label="Pivots")
            plt.plot(pivot_dates, pivot_prices, color="black", linestyle="--", alpha=0.6)
            
        plt.xlabel("Date")
        plt.ylabel("Price")
        plt.legend()
        plt.xticks(rotation=45)
        plt.grid()
    
class Profile(ABC):
    def __init__(self, data: pd.DataFrame, bin_size: int, perc: int):
        super().__init__()
        self.__data = data
        self.__bin_size = bin_size
        self.__perc = perc
        self.__profile: pd.DataFrame = None
        self.__poc = [None, None]
        self.__va = (None, None)
        
    @property
    def data(self):
        return self.__data
    
    @property
    def bin_size(self):
        return self.__bin_size
    
    @property
    def perc(self):
        return self.__perc
    
    @property
    def profile(self):
        return self.__profile 
    @profile.setter
    def profile(self, profile: pd.DataFrame):
        self.__profile = profile
        
    @property
    def poc(self):
        return self.__poc
    @poc.setter
    def poc(self, poc):
        self.__poc = poc
        
    @property
    def va(self):
        return self.__va
    @va.setter
    def va(self, va):
        self.__va = va
    
    @abstractmethod
    def fit(self):
        pass
    
    @abstractmethod
    def poc(self):
        pass
    
    @abstractmethod
    def value_area(self):
        pass
    
    @abstractmethod
    def plot(self):
        pass
    