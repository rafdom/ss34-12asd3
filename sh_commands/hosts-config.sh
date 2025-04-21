#!/bin/bash

# Configure routes on HostA
echo "Configuring routes on HostA..."
docker exec -it ha ip route del default
# Add a default route via R1
docker exec -it ha ip route add default via 10.0.14.4

# Configure routes on HostB
echo "Configuring routes on HostB..."
docker exec -it hb ip route del default
# Add a default route via R3
docker exec -it hb ip route add default via 10.0.15.4

echo "Host routes configured successfully!"