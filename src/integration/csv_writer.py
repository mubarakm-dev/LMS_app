import csv
import os
import re
from datetime import date, datetime

from src import config
from src.domain.errors import ServiceUnavailable

FORMULA_STARTS = ("=", "+", "-", "@", "\t", "\r")


def slug(text):
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")[:30] or "report"


def _cell(value):
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, str) and value.startswith(FORMULA_STARTS):
        return "'" + value
    return value


def write_csv(name, headers, rows):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(config.OUTPUT_DIR, f"{name}_{stamp}.csv")

    try:
        os.makedirs(config.OUTPUT_DIR, exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            for row in rows:
                writer.writerow([_cell(value) for value in row])
    except OSError:
        raise ServiceUnavailable(
            "Could not save the report. Check that the output folder is writable."
        )

    return os.path.abspath(path)
