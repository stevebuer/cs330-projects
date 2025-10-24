# Ham Radio DX Cluster Spots Dashboard

A Streamlit dashboard to query and display ham radio DX cluster spots from an API.

## Setup

1. Ensure Python 3.8+ is installed.
2. Create a virtual environment and activate it.
3. Install dependencies: `pip install streamlit requests pandas`

## Running the Dashboard

Run `streamlit run app.py` in the project directory.

The dashboard will open in your browser and display the spots fetched from the API.

## Configuration

- Update `API_URL` in `app.py` to point to your actual DX cluster API endpoint.
- Adjust the data processing based on the API response format.

## Notes

- Assumes the API returns a JSON list of spot objects.
- Customize the display as needed (e.g., add maps, filters).