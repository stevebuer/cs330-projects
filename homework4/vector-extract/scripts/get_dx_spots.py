#!/usr/bin/env python3
"""
Query the DX Cluster API and fetch all DX spots for a single day.

Usage examples:
  python scripts/get_dx_spots.py 2025-11-07 --output spots.json
  python scripts/get_dx_spots.py 2025-11-07 --format csv --output spots.csv

Assumptions:
- The API base URL defaults to the server in `openapi.yaml`: https://api.jxqz.org:8080/api
- Date is treated as UTC midnight-to-midnight (since YYYY-MM-DDT00:00:00Z until next day T00:00:00Z)
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from datetime import datetime, date, timedelta, timezone
from typing import List, Dict, Any

import requests


DEFAULT_BASE_URL = "https://api.jxqz.org:8080/api"
DEFAULT_LIMIT = 500  # per OpenAPI spec max 500


def iso_utc(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def fetch_spots_for_day(base_url: str, day: date, limit: int = DEFAULT_LIMIT) -> List[Dict[str, Any]]:
    since_dt = datetime(day.year, day.month, day.day, 0, 0, 0, tzinfo=timezone.utc)
    until_dt = since_dt + timedelta(days=1)
    since = iso_utc(since_dt)
    until = iso_utc(until_dt)

    collected: List[Dict[str, Any]] = []
    offset = 0

    session = requests.Session()

    while True:
        params = {"since": since, "until": until, "limit": limit, "offset": offset}
        url = base_url.rstrip("/") + "/spots"
        resp = session.get(url, params=params, timeout=30)
        try:
            resp.raise_for_status()
        except requests.HTTPError as e:
            raise RuntimeError(f"HTTP error while requesting {resp.url}: {e} - {resp.text}")

        data = resp.json()
        page_spots = data.get("spots") or []

        if not isinstance(page_spots, list):
            raise RuntimeError(f"Unexpected response format: 'spots' is not a list: {type(page_spots)}")

        collected.extend(page_spots)

        # Determine termination
        total_available = data.get("total_available")
        if total_available is not None:
            if len(collected) >= int(total_available):
                break
        # If API doesn't return total_available, stop when we get fewer than requested
        if len(page_spots) < limit:
            break

        # advance offset
        offset += len(page_spots)

    return collected


def spots_to_csv(spots: List[Dict[str, Any]], fp):
    # Choose a stable set of columns present in Spot schema
    fieldnames = [
        "id",
        "timestamp",
        "dx_call",
        "frequency",
        "spotter_call",
        "mode",
        "signal_report",
        "grid_square",
        "band",
        "comment",
    ]
    writer = csv.DictWriter(fp, fieldnames=fieldnames)
    writer.writeheader()
    for s in spots:
        # ensure only keys in fieldnames are written
        row = {k: s.get(k) for k in fieldnames}
        writer.writerow(row)


def parse_args():
    p = argparse.ArgumentParser(description="Fetch all DX spots for a single day from the DX Cluster API")
    p.add_argument("date", help="Date to fetch (YYYY-MM-DD)")
    p.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Base URL of the API (default from openapi.yaml)")
    p.add_argument("--limit", type=int, default=DEFAULT_LIMIT, help="Page size for requests (max 500)")
    p.add_argument("--format", choices=["json", "csv"], default="json", help="Output format")
    p.add_argument("--output", help="File to write output to (default stdout)")
    return p.parse_args()


def main():
    args = parse_args()

    # parse date
    try:
        day = datetime.strptime(args.date, "%Y-%m-%d").date()
    except ValueError:
        print("Invalid date format. Use YYYY-MM-DD.", file=sys.stderr)
        sys.exit(2)

    if args.limit < 1 or args.limit > 500:
        print("--limit must be between 1 and 500", file=sys.stderr)
        sys.exit(2)

    try:
        spots = fetch_spots_for_day(args.base_url, day, limit=args.limit)
    except Exception as e:
        print(f"Error fetching spots: {e}", file=sys.stderr)
        sys.exit(1)

    # output
    if args.output:
        f = open(args.output, "w", newline="", encoding="utf-8")
    else:
        f = sys.stdout

    try:
        if args.format == "json":
            json.dump(spots, f, ensure_ascii=False, indent=2)
            if f is not sys.stdout:
                f.write("\n")
        else:
            spots_to_csv(spots, f)
    finally:
        if args.output:
            f.close()


if __name__ == "__main__":
    main()
