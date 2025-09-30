#!/usr/bin/env python3
#
# DX Cluster Telnet Client with Text File Storage
# 

import telnetlib
import time

# DX Cluster server details
HOST = 'dx.k3lr.com'
PORT = 23

# Output file name
OUTPUT_FILE = 'dx_spots.txt'

def store_line(line):
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    with open(OUTPUT_FILE, 'a') as f:
        f.write(f"{timestamp}: {line}\n")

def main():
    print(f"Storing DX spots in {OUTPUT_FILE}")
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