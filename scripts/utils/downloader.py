import pandas as pd
from datetime import datetime, timedelta

from .ccxt_helpers import get_exchange, timeframe_to_seconds
from .datetime_helpers import dt_ts, dt_from_ts


# convert data downloaded to dataframe
def convert_to_dataframe(data: list[list]) -> pd.DataFrame:
    df = pd.DataFrame(data, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")
    df.set_index("Date", inplace=True)

    return df


# store data to csv file
def stored_csv(new_df: pd.DataFrame, symbol: str, timeframe: str) -> None:
    # Define CSV file path
    csv_file = f"./data/{symbol.lower()}{timeframe}.csv"

    # Load existing data if the file exists
    try:
        existing_df = pd.read_csv(csv_file, index_col=["Date"], parse_dates=["Date"])
    except FileNotFoundError:
        existing_df = pd.DataFrame()  # Create empty DataFrame if file doesn't exist

    # Combine old and new data, then remove duplicates
    combined_df = pd.concat([existing_df, new_df]).drop_duplicates()

    # Some case has some data duplicate index because ohlcv is difference, so,
    # to solve this issue is calculate average value price the data has same datetime
    combined_df = combined_df.groupby(combined_df.index).mean()

    # Save back to CSV (overwrite the file)
    combined_df.to_csv(csv_file)


# define number of data to fetch
def fetch_limits(start_date: datetime, end_date: datetime, timeframe: str, limit=1000):
    # Calculate the time difference
    gap = end_date - start_date

    total_seconds = gap.total_seconds()
    timeframe_second = timeframe_to_seconds(timeframe)

    size = int(total_seconds // timeframe_second)

    parts = [limit] * (size // limit)
    remainder = size % limit

    if remainder:
        parts.append(remainder)  # Add remainder if it exists

    return parts


# downloader
def downloader(
    exchange_id: str,
    symbol: str,
    start: str,
    end: str | None = None,
    timeframe: str = "5m",
    limit: int = 1000,
) -> pd.DataFrame:
    # using binance exchange to fetch
    binance = get_exchange(exchange_id)

    # convert start date and end date to timestamp
    start = datetime.fromisoformat(start)
    end = datetime.fromisoformat(end) if end is not None else datetime.now()

    if end is not None and start > end:
        raise ValueError("Start date cannot be greater than end date.")

    # convert start date to unix timestamp
    since = binance.parse8601(start.isoformat())

    # check exchange has fetch ohlcv data
    if binance.has["fetchOHLCV"]:
        ohlcv = []
        limits = fetch_limits(start, end, timeframe, limit)
        for limit in limits:
            if ohlcv:
                ts = dt_from_ts(ohlcv[-1][0]) + timedelta(
                    seconds=timeframe_to_seconds(timeframe)
                )
                since = dt_ts(ts)

            ohlcv_new = binance.fetch_ohlcv(symbol, timeframe, since, limit)
            ohlcv.extend(ohlcv_new)

        data = convert_to_dataframe(ohlcv)
        stored_csv(data, symbol, timeframe)

        return data
