from abc import ABC, abstractmethod


class PriceLevels(ABC):
    def __init__(self, threshold: float):
        self.__threshold = threshold / 100
        self.__pivots = []

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
    def fit(self, df):
        pass