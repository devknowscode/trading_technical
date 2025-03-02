from abc import ABC, abstractmethod
import pandas as pd


class __ProfileAnalyzer(ABC):
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
