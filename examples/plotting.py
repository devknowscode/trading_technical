import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.plotting import Plotting

plotter = Plotting(timeframe="1m")
plotter.live()
