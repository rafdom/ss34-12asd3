#!/usr/bin/env python3

import os
import subprocess
import argparse
import time
import sys

def run_command(command, silent=False):
    """Execute a shell command and optionally print output"""
    try:
        result = subprocess.run(command, shell=True, check=True, 
                                text=True, capture_output=True)
        if not silent and result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {command}")
        print(f"Error message: {e.stderr}")
        return False, e.stderr

def create_topology():
    """Create the network topology with Docker Compose"""
    print("Creating network topology...")
    
    # Navigate to the sh_commands directory
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../sh_commands"))
    
    # Build and start containers
    run_command("docker compose up -d")
    print("Waiting for containers to fully start...")
    time.sleep(5)
    
    print("Network topology created successfully!")
    return True

def configure_routers():
    """Install and configure OSPF on all routers"""
    print("Installing and configuring OSPF on all routers...")
    
    # Navigate to the sh_commands directory if not already there
    sh_commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../sh_commands")
    os.chdir(sh_commands_dir)
    
    # Install FRR on all routers
    run_command("./install-frr.sh")
    print("Waiting for FRR to initialize...")
    time.sleep(5)
    
    # Configure OSPF on all routers
    run_command("./configure-all-ospf.sh")
    print("Waiting for OSPF to converge...")
    time.sleep(10)
    
    print("OSPF configuration completed successfully!")
    return True

def configure_host_routes():
    """Configure routes on the hosts"""
    print("Configuring host routes...")
    
    # Navigate to the sh_commands directory if not already there
    sh_commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../sh_commands")
    os.chdir(sh_commands_dir)
    
    # Configure host routes
    run_command("./configure-host-routes.sh")
    time.sleep(2)
    
    print("Host routes configured successfully!")
    return True

def set_interface_cost(router, interface, cost):
    """Set OSPF cost for a specific interface on a router"""
    cmd = f"docker exec -it {router} vtysh -c 'configure terminal' -c 'interface {interface}' -c 'ip ospf cost {cost}' -c 'exit' -c 'write memory'"
    success, _ = run_command(cmd)
    return success

def move_traffic_north():
    """Configure network to prefer the north path (R1-R2-R3)"""
    print("Moving traffic to the north path (R1-R2-R3)...")
    
    # Set low cost on north path interfaces
    set_interface_cost("r1", "eth0", 10)  # R1-R2 interface
    set_interface_cost("r2", "eth0", 10)  # R2-R1 interface
    set_interface_cost("r2", "eth1", 10)  # R2-R3 interface
    set_interface_cost("r3", "eth0", 10)  # R3-R2 interface
    
    # Set high cost on south path interfaces
    set_interface_cost("r1", "eth1", 100)  # R1-R4 interface
    set_interface_cost("r4", "eth1", 100)  # R4-R1 interface
    set_interface_cost("r4", "eth0", 100)  # R4-R3 interface
    set_interface_cost("r3", "eth1", 100)  # R3-R4 interface
    
    # Wait for OSPF to converge
    print("Waiting for OSPF to converge...")
    time.sleep(10)
    
    # Verify the path with traceroute
    print("Verifying path with traceroute from HostA to HostB:")
    run_command("docker exec -it ha traceroute 10.0.15.3")
    
    print("Traffic successfully moved to the north path!")
    return True

def move_traffic_south():
    """Configure network to prefer the south path (R1-R4-R3)"""
    print("Moving traffic to the south path (R1-R4-R3)...")
    
    # Set high cost on north path interfaces
    set_interface_cost("r1", "eth0", 100)  # R1-R2 interface
    set_interface_cost("r2", "eth0", 100)  # R2-R1 interface
    set_interface_cost("r2", "eth1", 100)  # R2-R3 interface
    set_interface_cost("r3", "eth0", 100)  # R3-R2 interface
    
    # Set low cost on south path interfaces
    set_interface_cost("r1", "eth1", 10)  # R1-R4 interface
    set_interface_cost("r4", "eth1", 10)  # R4-R1 interface
    set_interface_cost("r4", "eth0", 10)  # R4-R3 interface
    set_interface_cost("r3", "eth1", 10)  # R3-R4 interface
    
    # Wait for OSPF to converge
    print("Waiting for OSPF to converge...")
    time.sleep(10)
    
    # Verify the path with traceroute
    print("Verifying path with traceroute from HostA to HostB:")
    run_command("docker exec -it ha traceroute 10.0.15.3")
    
    print("Traffic successfully moved to the south path!")
    return True

def test_connectivity():
    """Test network connectivity"""
    print("Testing network connectivity...")
    
    # Navigate to the sh_commands directory if not already there
    sh_commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../sh_commands")
    os.chdir(sh_commands_dir)
    
    # Run connectivity tests
    run_command("./test-connectivity.sh")
    
    print("Connectivity test completed!")
    return True

def get_current_path():
    """Determine the current path being used"""
    success, output = run_command("docker exec -it ha traceroute -n 10.0.15.3", silent=True)
    if success and "10.0.13.3" in output:
        return "south"  # R1-R4-R3 path
    else:
        return "north"  # R1-R2-R3 path

def toggle_path():
    """Toggle between north and south paths"""
    current_path = get_current_path()
    print(f"Current path is: {current_path}")
    
    if current_path == "north":
        move_traffic_south()
    else:
        move_traffic_north()
    
    return True

def main():
    """Main function to parse arguments and orchestrate the network"""
    parser = argparse.ArgumentParser(
        description="Network Orchestrator for managing traffic in a routed topology",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    # Define the mutually exclusive group for the main operations
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--create", action="store_true", 
                       help="Create the network topology")
    group.add_argument("--configure-ospf", action="store_true", 
                       help="Configure OSPF on all routers")
    group.add_argument("--host-routes", action="store_true", 
                       help="Configure routes on all hosts")
    group.add_argument("--north", action="store_true", 
                       help="Move traffic to the north path (R1-R2-R3)")
    group.add_argument("--south", action="store_true", 
                       help="Move traffic to the south path (R1-R4-R3)")
    group.add_argument("--toggle", action="store_true", 
                       help="Toggle between north and south paths")
    group.add_argument("--test", action="store_true", 
                       help="Test network connectivity")
    group.add_argument("--setup-all", action="store_true", 
                       help="Run complete setup (create topology, configure OSPF, set host routes)")
    
    args = parser.parse_args()
    
    # Execute the selected operation
    if args.create:
        create_topology()
    elif args.configure_ospf:
        configure_routers()
    elif args.host_routes:
        configure_host_routes()
    elif args.north:
        move_traffic_north()
    elif args.south:
        move_traffic_south()
    elif args.toggle:
        toggle_path()
    elif args.test:
        test_connectivity()
    elif args.setup_all:
        create_topology()
        configure_routers()
        configure_host_routes()
        test_connectivity()
        print("\nNetwork setup complete. Current path:")
        current_path = get_current_path()
        print(f"Using the {current_path} path (R1-{'R2-R3' if current_path == 'north' else 'R4-R3'})")

if __name__ == "__main__":
    main()