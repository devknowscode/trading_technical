import ccxt
from ccxt.base.types import Any


def get_exchange(exchange_id: str) -> Any:
    """
    Configure exchange by id to get from ccxt ('binance', 'okx', 'kucoin', etc..)
    """
    exchange_class = getattr(ccxt, exchange_id)
    exchange = exchange_class({})
    return exchange


def timeframe_to_seconds(timeframe: str) -> int:
    """
    Translates the timeframe interval value written in the human readable
    form ('1m', '5m', '1h', '1d', '1w', etc.) to the number
    of seconds for one timeframe interval.
    """
    return ccxt.Exchange.parse_timeframe(timeframe)
