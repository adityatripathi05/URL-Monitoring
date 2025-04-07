# backend\utils\logging.py
import logging
import os
import datetime

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.datetime.fromtimestamp(record.created, datetime.timezone.utc)
        if datefmt:
            s = dt.strftime(datefmt)
        else:
            t = dt.isoformat(timespec='milliseconds')
            s = "%sZ" % t
        return s

logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S.%fZ"
)

logger = logging.getLogger(__name__)
