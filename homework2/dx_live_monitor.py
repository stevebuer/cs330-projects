#!/usr/bin/env python3
#
# DX Cluster Live Monitor - Command Line Interface
# Usage: ./dx_live_monitor.py [callsign] [host] [port]
#

import sys
import os

def show_usage():
    print("DX Cluster Live Monitor - PostgreSQL Version")
    print("=" * 50)
    print("Usage: ./dx_live_monitor.py [callsign] [host] [port]")
    print("")
    print("Arguments:")
    print("  callsign  - Your amateur radio callsign (default: N7MKO)")
    print("  host      - DX cluster server hostname (default: dx.k3lr.com)")
    print("  port      - DX cluster server port (default: 23)")
    print("")
    print("Examples:")
    print("  ./dx_live_monitor.py                    # Use defaults")
    print("  ./dx_live_monitor.py W1AW               # Use callsign W1AW")
    print("  ./dx_live_monitor.py K1ABC dx.k3lr.com  # Custom callsign and host")
    print("")
    print("Environment Variables (create .env file):")
    print("  DB_HOST      - PostgreSQL host (default: localhost)")
    print("  DB_PORT      - PostgreSQL port (default: 5432)")
    print("  DB_NAME      - Database name (default: dxcluster)")
    print("  DB_USER      - Database user (default: postgres)")
    print("  DB_PASSWORD  - Database password")
    print("")
    print("Press Ctrl+C to stop monitoring")

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_usage()
        sys.exit(0)
    
    # Import and run the main script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, script_dir)
    
    try:
        from dx_cluster_live_pg import main
        main()
    except ImportError as e:
        print(f"Error importing dx_cluster_live_pg: {e}")
        print("Make sure dx_cluster_live_pg.py is in the same directory")
        sys.exit(1)