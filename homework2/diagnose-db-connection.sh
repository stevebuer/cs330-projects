#!/bin/bash

# Database Connection Troubleshooting Script
# Helps identify the correct database host for Docker containers

echo "=== Database Connection Troubleshooting ==="
echo ""

# Check if running in Docker
if [ -f /.dockerenv ]; then
    echo "✓ Running inside Docker container"
else
    echo "✗ Running on host machine"
fi

echo ""
echo "=== Network Information ==="

# Show various network options
echo "Host machine IP addresses:"
ip route get 8.8.8.8 2>/dev/null | grep -oP 'src \K\S+' || echo "  Could not detect"

echo ""
echo "Gateway IP (usually Docker host):"
ip route | grep default | awk '{print $3}' 2>/dev/null || echo "  Could not detect"

echo ""
echo "=== Database Connection Tests ==="

# Test different host options
test_hosts=("localhost" "host.docker.internal" "172.17.0.1" "$(ip route | grep default | awk '{print $3}' 2>/dev/null)")

for host in "${test_hosts[@]}"; do
    if [ -n "$host" ]; then
        echo -n "Testing $host:5432... "
        if command -v nc >/dev/null 2>&1; then
            if nc -z "$host" 5432 2>/dev/null; then
                echo "✓ REACHABLE"
            else
                echo "✗ NOT REACHABLE"
            fi
        elif command -v telnet >/dev/null 2>&1; then
            if timeout 3 telnet "$host" 5432 </dev/null 2>/dev/null | grep -q "Connected"; then
                echo "✓ REACHABLE"
            else
                echo "✗ NOT REACHABLE"
            fi
        else
            echo "? (no nc or telnet available)"
        fi
    fi
done

echo ""
echo "=== Environment Variables ==="
echo "PGHOST=${PGHOST:-not set}"
echo "PGPORT=${PGPORT:-not set}"
echo "PGDATABASE=${PGDATABASE:-not set}"
echo "PGUSER=${PGUSER:-not set}"

echo ""
echo "=== Recommendations ==="
echo "1. If PostgreSQL is on the Docker host, try:"
echo "   - PGHOST=host.docker.internal (if supported)"
echo "   - PGHOST=<host-ip-address>"
echo "   - Use network_mode: host in docker-compose"
echo ""
echo "2. If PostgreSQL is in another container:"
echo "   - Use the container name as PGHOST"
echo "   - Ensure containers are on the same network"
echo ""
echo "3. If PostgreSQL is on a remote server:"
echo "   - Use the server's IP address or hostname"
echo "   - Ensure firewall allows connections"