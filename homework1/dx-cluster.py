#!/usr/bin/env python3
#
# DX Cluster Telnet Client with SQLite Storage
# 

import telnetlib
import sqlite3
import time

# DX Cluster server details
HOST = 'dx.k3lr.com'
PORT = 23

# SQLite database setup
DB_NAME = 'dxcluster.db'
TABLE_NAME = 'dx_spots'

def setup_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f'''
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            line TEXT
        )
    ''')
    conn.commit()
    conn.close()

def store_line(line):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute(f'''
        INSERT INTO {TABLE_NAME} (timestamp, line)
        VALUES (?, ?)
    ''', (time.strftime('%Y-%m-%d %H:%M:%S'), line))
    conn.commit()
    conn.close()

def main():
    setup_database()
    with telnetlib.Telnet(HOST, PORT) as tn:
        print(f"Connected to {HOST}:{PORT}")
        tn.write(b'N7MKO\r\n')  # Send login callsign
        while True:
            try:
                data = tn.read_until(b'\n', timeout=10)
                line = data.decode('utf-8', errors='ignore').strip()
                if line:
                    print(line)
                    if line.startswith('DX'):
                        store_line(line)
            except Exception as e:
                print(f"Error: {e}")
                break

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nShutting down gracefully...")
        exit(0)
