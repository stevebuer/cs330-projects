# DX Cluster Live Monitor - PostgreSQL Version

This script combines the functionality of the original `dx-cluster.py` telnet client and `load_dx_spots_pg.py` database loader to create a real-time DX cluster monitor that connects directly to a DX cluster server and stores spots in a PostgreSQL database as they are received.

## Features

- **Real-time connection** to DX cluster servers via telnet
- **Live parsing** of DX spots as they arrive
- **PostgreSQL storage** with full spot parsing and analysis
- **Graceful shutdown** with Ctrl+C
- **Automatic reconnection** handling
- **Statistics tracking** for callsigns
- **Band detection** from frequency
- **Mode detection** from comments
- **Grid square extraction**
- **Signal report parsing**

## Files

- `dx_cluster_live_pg.py` - Main script with combined functionality
- `dx_live_monitor.py` - Command-line wrapper with help and usage info
- `load_dx_spots_pg.py` - Original file-based loader (still available)

## Prerequisites

1. PostgreSQL database with the DX cluster schema (from homework2)
2. Python packages: `psycopg2-binary`, `python-dotenv`
3. Network connection to DX cluster server

## Installation

```bash
# Install required Python packages
pip install psycopg2-binary python-dotenv

# Make scripts executable
chmod +x dx_cluster_live_pg.py
chmod +x dx_live_monitor.py
```

## Configuration

Create a `.env` file with your PostgreSQL connection details:

```bash
DB_HOST=localhost
DB_PORT=5432
DB_NAME=dxcluster
DB_USER=your_username
DB_PASSWORD=your_password
```

## Usage

### Basic Usage (with defaults)
```bash
./dx_live_monitor.py
```

### With Custom Callsign
```bash
./dx_live_monitor.py W1AW
```

### With Custom Server
```bash
./dx_live_monitor.py K1ABC dx.k3lr.com 23
```

### Direct Script Usage
```bash
./dx_cluster_live_pg.py [callsign] [host] [port]
```

## Default Settings

- **Callsign**: N7MKO
- **DX Cluster Server**: dx.k3lr.com:23
- **Database**: localhost:5432/dxcluster

## Output

The script will display:
- Connection status and initial server messages
- All incoming lines from the DX cluster
- Parsed and stored DX spots with details
- Periodic database commit confirmations
- Statistics on spots processed

Example output:
```
DX Cluster Live Monitor - PostgreSQL Version
Callsign: W1AW
Server: dx.k3lr.com:23
Database: localhost:5432/dxcluster
Press Ctrl+C to stop

Connected to PostgreSQL database
Connecting to dx.k3lr.com:23...
Connection established. Initial response:
...

Monitoring DX spots... (storing to database)
------------------------------------------------------------
14:23:45 | DX de W1AW:     14.205.0  JA1ABC       CQ DX                1423Z
  -> Stored spot #1: JA1ABC on 14205.0 by W1AW
14:23:48 | DX de K1DEF:    21.025.0  VK2GHI       599 in NSW           1423Z  
  -> Stored spot #2: VK2GHI on 21025.0 by K1DEF
```

## Database Schema

The script uses the same PostgreSQL schema as `load_dx_spots_pg.py`:

- `raw_spots` - Original text lines with timestamps
- `dx_spots` - Parsed spot data with extracted fields
- `callsigns` - Statistics for spotted and spotting callsigns

## Parsed Fields

For each DX spot, the following fields are extracted and stored:

- **timestamp** - When the spot was received (UTC)
- **dx_call** - Callsign being spotted
- **frequency** - Frequency in kHz
- **spotter_call** - Callsign of the spotter
- **comment** - Additional information
- **mode** - Detected mode (CW, SSB, FT8, etc.)
- **band** - Amateur radio band (20m, 40m, etc.)
- **signal_report** - Signal strength if present
- **grid_square** - Grid locator if present

## Error Handling

- **Connection failures**: Displays error and exits gracefully
- **Database errors**: Logs errors but continues monitoring
- **Parse errors**: Skips malformed lines and continues
- **Keyboard interrupt**: Commits pending data before shutdown

## Monitoring Tips

1. **Run in screen/tmux** for long-term monitoring
2. **Monitor database growth** as spots accumulate quickly
3. **Use Ctrl+C** for clean shutdown to ensure data integrity
4. **Check .env file** if connection fails

## Differences from Original Scripts

### From dx-cluster.py:
- Uses PostgreSQL instead of SQLite
- Parses spots in real-time instead of just storing raw text
- Adds comprehensive error handling and graceful shutdown

### From load_dx_spots_pg.py:
- Reads from telnet connection instead of files
- Processes spots immediately as received
- Adds live timestamps since cluster doesn't provide them

## Troubleshooting

### Connection Issues
- Verify network connectivity to DX cluster server
- Check if firewall blocks telnet (port 23)
- Try alternative DX cluster servers

### Database Issues  
- Verify PostgreSQL connection settings in `.env`
- Check database permissions for the user
- Ensure the DX cluster schema exists

### Performance
- Monitor database size and consider periodic cleanup
- Adjust commit frequency for high-volume periods
- Consider indexing strategy for large datasets