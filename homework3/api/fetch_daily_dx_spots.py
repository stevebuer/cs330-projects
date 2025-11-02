"""
Fetch daily DX spot data from the DX Cluster API and aggregate into daily summaries for ML modeling.
"""
import requests
import pandas as pd
from datetime import datetime, timedelta

API_BASE = "http://dx.jxqz.org:8080/api/spots"

# Set your date range here
START_DATE = "2025-09-01"  # YYYY-MM-DD
END_DATE = "2025-10-30"    # YYYY-MM-DD


def fetch_spots_for_day(date_str):
    since = f"{date_str}T00:00:00Z"
    until = f"{date_str}T23:59:59Z"
    params = {
        "since": since,
        "until": until,
        "limit": 500  # max per request
    }
    spots = []
    offset = 0
    while True:
        params["offset"] = offset
        resp = requests.get(API_BASE, params=params)
        resp.raise_for_status()
        data = resp.json()
        spots.extend(data.get("spots", []))
        if len(data.get("spots", [])) < params["limit"]:
            break
        offset += params["limit"]
    return spots


def aggregate_daily(spots):
    df = pd.DataFrame(spots)
    summary = {
        "total_spots": len(df),
        "unique_dx_stations": df["dx_call"].nunique() if "dx_call" in df else 0,
        "unique_spotters": df["spotter_call"].nunique() if "spotter_call" in df else 0,
        "bands": df["band"].value_counts().to_dict() if "band" in df else {},
        "modes": df["mode"].value_counts().to_dict() if "mode" in df else {},
    }
    return summary


def main():
    start = datetime.strptime(START_DATE, "%Y-%m-%d")
    end = datetime.strptime(END_DATE, "%Y-%m-%d")
    all_summaries = []
    for n in range((end - start).days + 1):
        day = start + timedelta(days=n)
        date_str = day.strftime("%Y-%m-%d")
        print(f"Fetching spots for {date_str}...")
        spots = fetch_spots_for_day(date_str)
        summary = aggregate_daily(spots)
        summary["date"] = date_str
        all_summaries.append(summary)
    df_summary = pd.DataFrame(all_summaries)
    df_summary.to_csv("daily_dx_spot_summary.csv", index=False)
    print("Saved daily summaries to daily_dx_spot_summary.csv")


if __name__ == "__main__":
    main()
