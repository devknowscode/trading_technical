import time
from datetime import datetime, timezone


def dt_ts(dt: datetime | None = None) -> int:
    """
    Return dt in ms as a timestamp in UTC.
    If dt is None, return the current datetime in UTC.
    """
    if dt:
        return int(dt.timestamp() * 1000)
    return int(time() * 1000)


def dt_from_ts(timestamp: float) -> datetime:
    """
    Return a datetime from a timestamp.
    :param timestamp: timestamp in seconds or milliseconds
    """
    if timestamp > 1e10:
        # Timezone in ms - convert to seconds
        timestamp /= 1000
    return datetime.fromtimestamp(timestamp, tz=timezone.utc)
