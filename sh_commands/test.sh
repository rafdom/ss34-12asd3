#!/bin/bash

# Test connectivity between directly connected routers
echo "=== Testing Direct Router Connectivity ==="
echo "R1 → R2:"
docker exec -it r1 ping -c 2 10.0.10.3
echo "R1 → R4:"
docker exec -it r1 ping -c 2 10.0.13.3
echo "R2 → R3:"
docker exec -it r2 ping -c 2 10.0.11.4
echo "R3 → R4:"
docker exec -it r3 ping -c 2 10.0.12.4

# Test connectivity between hosts and directly connected routers
echo "=== Testing Host-Router Connectivity ==="
echo "HostA → R1:"
docker exec -it ha ping -c 2 10.0.14.4
echo "HostB → R3:"
docker exec -it hb ping -c 2 10.0.15.4

# Verify IP forwarding is enabled on all routers
echo "=== Verifying IP Forwarding ==="
for router in r1 r2 r3 r4; do
  echo "IP forwarding on $router:"
  docker exec -it $router sysctl net.ipv4.ip_forward
  echo "-------------------"
done

# Test end-to-end connectivity
echo "=== Testing End-to-End Connectivity ==="
echo "HostA → HostB:"
docker exec -it ha ping -c 4 10.0.15.3

# Show path packets take
echo "=== Traceroute from HostA to HostB ==="
docker exec -it ha traceroute 10.0.15.3

echo "Verification complete!"