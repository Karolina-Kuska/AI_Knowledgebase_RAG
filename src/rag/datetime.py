from datetime import datetime
from zoneinfo import ZoneInfo

def now_warsaw():
    tz = ZoneInfo("Europe/Warsaw")
    dt = datetime.now(tz)
    return {
        "date": dt.strftime("%Y-%m-%d"),
        "time": dt.strftime("%H:%M"),
        "weekday_pl": ["pon","wt","śr","czw","pt","sob","nd"][dt.weekday()]
    }
