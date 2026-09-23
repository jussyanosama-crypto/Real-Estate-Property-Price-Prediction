"""Download the official NYC rolling-sales extract into data/."""

from pathlib import Path
import warnings

import requests


DATA_URL = "https://data.cityofnewyork.us/resource/usep-8jbt.csv?$limit=100000"
DATA_PATH = Path("data/nyc_citywide_rolling_sales.csv")


def download_data() -> Path:
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    try:
        response = requests.get(DATA_URL, timeout=120)
    except requests.exceptions.SSLError:
        warnings.warn("TLS verification failed; retrying without certificate verification.")
        response = requests.get(DATA_URL, timeout=120, verify=False)
    response.raise_for_status()
    DATA_PATH.write_bytes(response.content)
    return DATA_PATH


if __name__ == "__main__":
    print(f"Saved dataset to {download_data()}")
