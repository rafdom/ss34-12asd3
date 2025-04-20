import subprocess
import time

def run_cmd(cmd):
    print(f"\n[Running] {cmd}")
    subprocess.run(cmd, shell=True)

# ------------------
# SHIFT TO R1 -> R2 -> R3
# ------------------
print("\n=== Switching to R1 -> R2 -> R3 Path ===")
time.sleep(1)

# R1: favor R2
run_cmd('docker exec r1 vtysh -c "configure terminal" -c "interface eth2" -c "ip ospf cost 5"')  # eth2: 10.0.10.4
run_cmd('docker exec r1 vtysh -c "configure terminal" -c "interface eth0" -c "ip ospf cost 20"') # eth0: 10.0.13.4

# R2: both interfaces to 5
run_cmd('docker exec r2 vtysh -c "configure terminal" -c "interface eth0" -c "ip ospf cost 5"')  # eth0: 10.0.10.3
run_cmd('docker exec r2 vtysh -c "configure terminal" -c "interface eth1" -c "ip ospf cost 5"')  # eth1: 10.0.11.3

# R3: align with R2 path (lower cost on eth1)
run_cmd('docker exec r3 vtysh -c "configure terminal" -c "interface eth1" -c "ip ospf cost 5"')  # eth1: 10.0.11.4
run_cmd('docker exec r3 vtysh -c "configure terminal" -c "interface eth0" -c "ip ospf cost 20"')  # eth0: 10.0.12.3

# ------------------
# SHIFT TO R1 -> R4 -> R3
# ------------------
time.sleep(5)
print("\n=== Switching to R1 -> R4 -> R3 Path ===")

# R1: favor R4
run_cmd('docker exec r1 vtysh -c "configure terminal" -c "interface eth2" -c "ip ospf cost 20"')  # eth2: 10.0.10.4
run_cmd('docker exec r1 vtysh -c "configure terminal" -c "interface eth0" -c "ip ospf cost 5"')   # eth0: 10.0.13.4

# R4: both interfaces to 5
run_cmd('docker exec r4 vtysh -c "configure terminal" -c "interface eth0" -c "ip ospf cost 5"')   # eth0: 10.0.13.3
run_cmd('docker exec r4 vtysh -c "configure terminal" -c "interface eth1" -c "ip ospf cost 5"')   # eth1: 10.0.12.4

# R3: align with R4 path (lower cost on eth0)
run_cmd('docker exec r3 vtysh -c "configure terminal" -c "interface eth1" -c "ip ospf cost 20"')  # eth1: 10.0.11.4
run_cmd('docker exec r3 vtysh -c "configure terminal" -c "interface eth0" -c "ip ospf cost 5"')   # eth0: 10.0.12.3

print("\n=== Done adjusting OSPF link costs ===")
