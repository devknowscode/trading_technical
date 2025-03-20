import pandas as pd
from typing import Union

from importlib import resources as pkg_resources

from bokeh.io import curdoc, output_notebook
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot, layout
from bokeh.transform import factor_cmap
from bokeh.models import (
    ColumnDataSource,
    CustomJS,
    HoverTool,
    CrosshairTool,
    NumeralTickFormatter,
    DatetimeTickFormatter,
)
from bokeh.models.annotations import Title

from scripts import package_data as pkgdata


class Plotter:
    """Automated trading chart generator

    Methods
    --------
    configure()
        Configure the plot settings.

    add_tool(tool_name)
        Add bokeh tool to plot. This add the tool_name string to the fig_tools attribute.

    plot()
        Creates a trading chart of OHLC price data and indicators.
    """

    def __init__(self, data: Union[pd.Series, pd.DataFrame] = None):
        self._chart_theme = "caliber"
        self._max_graph_over = 3
        self._max_graph_below = 2
        self._fig_tools = "pan,wheel_zoom,box_zoom,undo,redo,reset,save,crosshair"
        self._ohlc_height = 400
        self._ohlc_width = 800
        self._top_fig_height = 150
        self._bottom_fig_height = 150
        self._jupyter_notebook = False
        self._line_chart = False

        if data is None:
            raise ValueError("Data is required but missing!")

        if isinstance(data, pd.Series):
            self._data = self._reindex_data(data)
            self._line_chart = True
        elif isinstance(data, pd.DataFrame):
            self._data = self._reindex_data(data)
        else:
            raise Exception(f"Unrecognised data type pass to Plot ({type(data)})")

        # Load Javascript code for auto-scaling
        self._autoscale_args = {}
        self._autoscale_code = pkg_resources.read_text(pkgdata, "autoscale.js")

    def add_tool(self, tool_name: str):
        """Adds a tool to the plot.

        Parameters
        ----------
        tool_name : str
            The name of tool to add (see Bokeh documentation).

        Returns
        -------
        None
            The tool will be added to the chart produced.

        """

        self._fig_tools = self._fig_tools + "," + tool_name

    def configure(
        self,
        max_graph_over: int = None,
        max_graph_below: int = None,
        fig_tools: str = None,
        ohlc_height: int = None,
        ohlc_width: int = None,
        top_fig_height: int = None,
        bottom_fig_height: int = None,
        jupyter_notebook: bool = None,
        chart_theme: str = None,
    ) -> None:
        """Configures the plot settings.

        Parameters
        ----------
        max_graph_over : int, optional
            Maximum number of indicators overlaid on the main chart. The
            default is 3.

        max_graph_below : int, optional
            Maximum number of indicators below the main chart. The default is 2.

        fig_tools : str, optional
            The figure tools. The default is "pan,wheel_zoom,box_zoom,undo,
            redo,reset,save,crosshair".

        ohlc_height : int, optional
            The height (px) of the main chart. The default is 400.

        ohlc_width : int, optional
            The width (px) of the main chart. The default is 800.

        top_fig_height : int, optional
            The height (px) of the figure above the main chart. The default is 150.

        bottom_fig_height : int, optional
            The height (px) of the figure(s) below the main chart. The default is 150.

        chart_theme : bool, optional
            The theme of the Bokeh chart generated. The default is "caliber".

        Returns
        -------
        None
            The plot settings will be saved to the active Plotter instance.

        """

        self._max_graph_over = (
            max_graph_over if max_graph_over is not None else self._max_graph_over
        )
        self._max_graph_below = (
            max_graph_below if max_graph_below is not None else self._max_graph_below
        )
        self._fig_tools = fig_tools if fig_tools is not None else self._fig_tools
        self._ohlc_height = (
            ohlc_height if ohlc_height is not None else self._ohlc_height
        )
        self._ohlc_width = ohlc_width if ohlc_width is not None else self._ohlc_width
        self._top_fig_height = (
            top_fig_height if top_fig_height is not None else self._top_fig_height
        )
        self._bottom_fig_height = (
            bottom_fig_height
            if bottom_fig_height is not None
            else self._bottom_fig_height
        )
        self._jupyter_notebook = (
            jupyter_notebook if jupyter_notebook is not None else self._jupyter_notebook
        )
        self._chart_theme = (
            chart_theme if chart_theme is not None else self._chart_theme
        )

    def plot(
        self, instrument: str = None, indicators: dict = None, show_fig: bool = True
    ) -> None:
        """Creates a trading chart of OHLC price data and indicators."""
        if instrument is None:
            title_string = "Plotter IndiView"
        else:
            title_string = f"Plotter IndiView - {instrument}"
        output_file("./output/web/indiview-chart.html", title=title_string)

        # Add base data
        source = ColumnDataSource(self._data)

        # Main plot
        if self._line_chart:
            source.add(self._data.plot_data, "High")
            source.add(self._data.plot_data, "Low")
            main_plot = self._create_main_plot(source)
        else:
            source.add(
                (self._data["Close"] >= self._data["Open"])
                .values.astype("uint8")
                .astype(str),
                "change",
            )
            main_plot = self._plot_candle(source)

        # Initialize auto scale arguments
        self._autoscale_args = {"y_range": main_plot.y_range, "source": source}

        # Indicators
        bottom_figs = []
        if indicators is not None:
            bottom_figs = self._plot_indicators(indicators, main_plot)

        # Auto-sacle y-axis of candlestick chart
        callback = CustomJS(args=self._autoscale_args, code=self._autoscale_code)
        main_plot.x_range.js_on_change("end", callback)

        # Compile plots for final figure
        plots = [main_plot] + bottom_figs
        linked_crosshair = CrosshairTool(dimensions="both")

        titled = 0
        t = Title()
        t.text = title_string
        for plot in plots:
            if plot is not None:
                plot.xaxis.major_label_overrides = {
                    i: date.strftime("%b %d %Y")
                    for i, date in enumerate(pd.to_datetime(self._data["Date"]))
                }
                plot.xaxis.bounds = (0, self._data.index[-1])
                plot.sizing_mode = "stretch_width"

                if titled == 0:
                    plot.title = t
                    titled = 1

                plot.add_tools(linked_crosshair)

        # Construct final figure
        fig = gridplot(
            plots,
            ncols=1,
            toolbar_location="right",
            toolbar_options=dict(logo=None),
            merge_tools=True,
        )
        fig.sizing_mode = "stretch_width"

        # Set theme
        curdoc().theme = self._chart_theme

        if show_fig:
            if self._jupyter_notebook:
                output_notebook()
            show(fig)

    def _reindex_data(self, data: Union[pd.DataFrame, pd.Series]) -> pd.DataFrame:
        if isinstance(data, pd.Series):
            modified_data = data.to_frame(name="plot_data")
        elif isinstance(data, pd.DataFrame):
            modified_data = data.copy()
        modified_data["Date"] = modified_data.index
        modified_data = modified_data.reset_index(drop=True)
        modified_data["data_index"] = modified_data.index
        return modified_data

    def _create_main_plot(
        self,
        source: ColumnDataSource,
        line_color: str = "black",
    ):
        fig = figure(
            width=self._ohlc_width,
            height=self._ohlc_height,
            title="Custom Plot Data",
            tools=self._fig_tools,
            active_drag="pan",
            active_scroll="wheel_zoom",
        )

        fig.line("data_index", "plot_data", line_color=line_color, source=source)

        return fig

    def _plot_candle(self, source: ColumnDataSource):
        """Plot OHLC data onto new figure"""
        bull_colour = "#D5E1DD"
        bear_colour = "#F2583E"
        candle_colours = [bear_colour, bull_colour]
        colour_map = factor_cmap("change", candle_colours, ["0", "1"])

        candle_tooltips = [
            ("Date", "@Date{%a %b %d '%y %H:%M:%S}"),
            ("Open", "@Open{0,0.00}"),
            ("High", "@High{0,0.00}"),
            ("Low", "@Low{0,0.00}"),
            ("Close", "@Close{0,0.00}"),
        ]

        candle_plot = figure(
            width=self._ohlc_width,
            height=self._ohlc_height,
            tools=self._fig_tools,
            active_drag="pan",
            active_scroll="wheel_zoom",
        )

        candle_plot.segment(
            "index", "High", "index", "Low", color="black", source=source
        )
        candles = candle_plot.vbar(
            "index",
            0.7,
            "Open",
            "Close",
            source=source,
            line_color="black",
            fill_color=colour_map,
        )

        candle_hovertool = HoverTool(
            tooltips=candle_tooltips,
            formatters={"@Date": "datetime"},
            mode="vline",
            renderers=[candles],
        )

        candle_plot.add_tools(candle_hovertool)

        return candle_plot

    def _plot_indicators(self, indicators: dict, linked_fig):
        """
        Plot indicators based on indicator type. If indicator type is `over`, it will be plotted on top
        of `linked_fig`. If indicator type is `below`, it will be plotted on a new figure below the OHLC chart.
        """
        plot_type = {
            "MACD": "below",
            "MA": "over",
            "RSI": "below",
        }

        # Plot indicators
        graph_over = 0
        graph_below = 0
        bottom_figs = []
        colours = ["red", "blue", "orange", "green", "black", "yellow"]

        for indicator in indicators:
            indi_type = indicator[indicator]["type"]

            if indi_type in plot_type:
                if plot_type[indi_type] == "over" and graph_over < self._max_graph_over:
                    if isinstance(indicators[indicator]["data"], pd.Series):
                        # Timeseries provided, merge indexes
                        if indicators[indicator]["data"].name is None:
                            indicators[indicator]["data"].name = "data"
                        merged_indicator_data = pd.merge(
                            self._data,
                            indicators[indicator]["data"],
                            left_on="Date",
                            right_index=True,
                        )
                        line_data = merged_indicator_data[
                            indicators[indicator]["data"].name
                        ]
                        x_vals = line_data.index
                        y_vals = line_data.values
                    else:
                        raise Exception("Plot data must be a timeseries.")

                    linked_fig.line(
                        x_vals,
                        y_vals,
                        line_width=1.5,
                        legend_label=indicator,
                        line_color=(
                            indicators[indicator]["color"]
                            if "color" in indicators[indicator]
                            else colours[graph_over]
                        ),
                    )
                    graph_over += 1
                elif (
                    plot_type[indi_type] == "below"
                    and graph_below < self._max_graph_below
                ):
                    if isinstance(indicator[indicator]["data"], pd.Series):
                        # Timeseries provided, merge indexes
                        if indicators[indicator]["data"].name is None:
                            indicators[indicator]["data"].name = "data"
                        line_source = self._create_line_source(
                            indicators[indicator]["data"]
                        )
                    else:
                        raise Exception("Plot data must be a timeseries.")

                    new_fig = self._plot_line(
                        line_source,
                        linked_fig,
                        indicators[indicator]["data"].name,
                        new_fig=True,
                        legend_label=indicator,
                        fig_height=130,
                    )
                    self._add_to_autoscale_args(line_source, new_fig.y_range)

                    graph_below += 1
                    bottom_figs.append(new_fig)
            else:
                # The indicator plot type is not recognised - plotting on new fig
                if graph_below < self._max_graph_below:
                    print(f"Indicator type {indi_type} not recognised in Plotter.")
                    line_source = self._create_line_source(
                        indicators[indicator]["data"]
                    )
                    new_fig = self._plot_line(
                        line_source,
                        linked_fig,
                        indicators[indicator]["data"].name,
                        new_fig=True,
                        fig_height=130,
                    )
                    self._add_to_autoscale_args(line_source, new_fig.y_range)

                    graph_below += 1
                    bottom_figs.append(new_fig)

        return bottom_figs

    def _plot_line(
        self,
        source: ColumnDataSource,
        linked_fig,
        column_name: str,
        new_fig: bool = False,
        fig_height: float = 150,
        fig_title: str = None,
        line_colour: str = "black",
    ):
        if new_fig:
            fig = figure(
                width=linked_fig.width,
                height=fig_height,
                title=fig_title,
                tools=self._fig_tools,
                active_drag="pan",
                active_scroll="wheel_zoom",
                x_range=linked_fig.x_range,
            )
        else:
            fig = linked_fig

        fig.line("data_index", column_name, line_color=line_colour, source=source)

        return fig

    def _add_to_autoscale_args(self, source: ColumnDataSource, y_range):
        """
        Parameters
        ----------
        source : ColumnDataSource
            The column data source.

        y_range : Bokeh Range
            The y_range attribute of the chart.

        """
        added = False
        range_key = "bottom_range_1"
        source_key = "bottom_source_1"
        while not added:
            if range_key not in self._autoscale_args:
                # Keys can be added
                self._autoscale_args[range_key] = y_range
                self._autoscale_args[source_key] = source
                added = True
            else:
                # Increment key
                range_key = range_key[:-1] + str(int(range_key[-1]) + 1)
                source_key = source_key[:-1] + str(int(source_key[-1]) + 1)

    def _create_line_source(self, indicator_data):
        """Create ColumnDataSource from indicator line data."""
        # Overwrite indicator data name to prevent conflict
        data_name = "plot_data"
        indicator_data.name = data_name
        merged_indicator_data = pd.merge(
            self._data, indicator_data, left_on="Date", right_index=True
        )
        merged_indicator_data.fillna(method="bfill", inplace=True)
        data_name = indicator_data.name
        line_source = ColumnDataSource(merged_indicator_data[[data_name, "data_index"]])
        line_source.add(merged_indicator_data[data_name].values, "High")
        line_source.add(merged_indicator_data[data_name].values, "Low")
        return line_source


if __name__ == "__main__":
    data = pd.read_csv("./data/btcusdt4h.csv", index_col=["Date"], parse_dates=["Date"])
    p = Plotter(data)
    p.plot()
