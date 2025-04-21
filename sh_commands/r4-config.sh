#!/bin/bash

# Configure OSPF on R4
docker exec -it r4 vtysh -c 'configure terminal' -c 'router ospf' -c 'ospf router-id 4.4.4.4' -c 'network 10.0.12.0/24 area 0' -c 'network 10.0.13.0/24 area 0' -c 'exit'
docker exec -it r4 vtysh -c 'configure terminal' -c 'interface eth0' -c 'ip ospf area 0' -c 'ip ospf cost 20' -c 'exit' -c 'interface eth1' -c 'ip ospf area 0' -c 'ip ospf cost 20' -c 'exit'
docker exec -it r4 vtysh -c 'configure terminal' -c 'debug ospf packet all' -c 'exit'
docker exec -it r4 vtysh -c 'write memory'
docker exec -it r4 vtysh -c 'show running-config'