# DX Query helper

Small helper script to fetch DX cluster "spots" for a single day using the project's OpenAPI endpoints.

Requirements
- Python 3.8+
- Install dependencies:

  pip install -r requirements.txt

Usage

- Fetch spots for a given date (YYYY-MM-DD) and print JSON to stdout:

  python scripts/get_dx_spots.py 2025-11-07

- Save JSON to a file:

  python scripts/get_dx_spots.py 2025-11-07 --output spots-2025-11-07.json

- Save as CSV:

  python scripts/get_dx_spots.py 2025-11-07 --format csv --output spots-2025-11-07.csv

Options
- `--base-url` — override the API base URL (defaults to the server in `openapi.yaml`).
- `--limit` — page size per request (default 500, max 500 per API spec).

Notes and assumptions
- The script uses UTC midnight-to-midnight for the requested date (since YYYY-MM-DDT00:00:00Z until next day at T00:00:00Z).
- The API supports `since` and `until` ISO datetimes and pagination (limit & offset). The script paginates until all spots are fetched.

If you want, I can:
- Add authentication support if your API requires it.
- Add unit tests that mock API responses and validate pagination.
