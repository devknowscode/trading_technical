import pandas as pd
import ccxt
from ccxt.base.types import Any

# config exchange
def get_exchange(exchange_id: str) -> Any:
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({})
    return exchange

# convert data downloaded to dataframe
def convert_to_dataframe(data: list[list]) -> pd.DataFrame:
    df = pd.DataFrame(ohlcv, columns=["Date", "Open", "High", "Low", "Close", "Volume"])
    df["Date"] = pd.to_datetime(df["Date"], unit="ms")
    df = df.set_index("Date")
    return df

# store data to csv file
def stored_csv(df: pd.DataFrame, symbol: str, timeframe: str) -> None:
    df.to_csv(f"./data/{symbol.lower()}{timeframe}.csv")
    
if __name__ == '__main__':
    # using binance exchange to fetch
    binance = get_exchange("binance")
    
    symbol = "BTCUSDT"
    timeframe = "4h"

    # check exchange has fetch ohlcv data
    if binance.has["fetchOHLCV"]:
        ohlcv = binance.fetch_ohlcv(symbol, timeframe, limit=1000)
        data = convert_to_dataframe(ohlcv)
        stored_csv(data, symbol, timeframe)
