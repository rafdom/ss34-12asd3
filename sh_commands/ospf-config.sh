#!/bin/bash

# Restart FRR on all routers to ensure clean state
echo "Restarting FRR on all routers..."
for router in r1 r2 r3 r4; do
  docker exec -it $router service frr restart
  echo "Restarted FRR on $router"
done

# Wait for a few seconds to ensure FRR is up
sleep 5

echo "trying to configure routers"
./r1-config.sh
./r2-config.sh
./r3-config.sh
./r4-config.sh

# Wait for OSPF to converge
echo "Waiting for OSPF to converge..."
sleep 10

echo "heres the OSPF neighbors:"
for router in r1 r2 r3 r4; do
  echo "OSPF neighbors on $router:"
  docker exec -it $router vtysh -c 'show ip ospf neighbor'
  echo "-------------------"
done

echo "heres the routes:"
for router in r1 r2 r3 r4; do
  echo "OSPF routes on $router:"
  docker exec -it $router vtysh -c 'show ip route'
  echo "-------------------"
done

echo "finished ospf-config.sh"