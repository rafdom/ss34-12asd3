# Dom Johansen, u1304418, python code to orchestrate the network using scripts
#!/usr/bin/env python3

import os
import subprocess
import argparse
import time
import sys

def run_command(command, silent=False):
    """Execute shell command and return output of the command"""
    try:
        result = subprocess.run(command, shell=True, check=True, text=True, capture_output=True)
        if not silent and result.stdout:
            print(result.stdout)
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, e.stderr

def create_topology():
    """method to create the network topology"""

    # Navigate to the sh_commands
    os.chdir(os.path.join(os.path.dirname(os.path.abspath(__file__)), "sh_commands"))
    
    # Build and start containers
    run_command("docker compose up -d")
    print("giving countainer a second")
    time.sleep(7)
    
    print("topology created")
    return True

def configure_routers():
    """method to configure OSPF on all routers"""
    print("trying to configure OSPF on routers")
    
    # Navigate to the sh_commands
    sh_commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sh_commands")
    os.chdir(sh_commands_dir)

    # call sh script to install frr
    run_command("./install-frr.sh")
    time.sleep(7)
    
    # Configure OSPF on all routers
    run_command("./ospf-config.sh")
    print("Waiting for OSPF to converge...")
    time.sleep(10)
    
    print("OSPF configuration completed successfully!")
    return True

def configure_host_routes():
    """method to configure host routes"""
    print("trying to configure host routes")
    
    # Navigate to the sh_commands
    sh_commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sh_commands")
    os.chdir(sh_commands_dir)
    
    # call sh script to install routes
    run_command("./host-config.sh")
    time.sleep(5)
    
    print("host routes configured")
    return True

def set_interface_cost(router, interface, cost):
    """setting cost of the interface"""
    cmd = f"docker exec -it {router} vtysh -c 'configure terminal' -c 'interface {interface}' -c 'ip ospf cost {cost}' -c 'exit' -c 'write memory'"
    success, _ = run_command(cmd)
    return success

def move_traffic_north():
    """moving traffic to the north path"""
    print("Moving north")
    # Set low cost on north path interfaces
    set_interface_cost("r1", "eth0", 10)  
    set_interface_cost("r2", "eth0", 10)  
    set_interface_cost("r2", "eth1", 10)  
    set_interface_cost("r3", "eth0", 10)  
    
    # Set high cost on south path interfaces
    set_interface_cost("r1", "eth1", 150)  
    set_interface_cost("r4", "eth1", 150)  
    set_interface_cost("r4", "eth0", 150)  
    set_interface_cost("r3", "eth1", 150)  
    
    print("Waiting for OSPF to converge")
    time.sleep(10)
    
    # Verify the path with traceroute
    print("pinging from HostA to HostB")
    run_command("docker exec -it ha traceroute 10.0.15.3")
    
    print("worked moving north")
    return True

def move_traffic_south():
    """moving traffic to the south path"""
    print("moving south")
    
    # Set high cost on north path interfaces
    set_interface_cost("r1", "eth0", 150) 
    set_interface_cost("r2", "eth0", 150) 
    set_interface_cost("r2", "eth1", 150)
    set_interface_cost("r3", "eth0", 150) 
    
    # Set low cost on south path interfaces
    set_interface_cost("r1", "eth1", 10)  
    set_interface_cost("r4", "eth1", 10) 
    set_interface_cost("r4", "eth0", 10) 
    set_interface_cost("r3", "eth1", 10)  
    
    # Wait for OSPF to converge
    print("Waiting for OSPF to converge...")
    time.sleep(10)
    
    # Verify the path with traceroute
    print("pinging from HostA to HostB")
    run_command("docker exec -it ha traceroute 10.0.15.3")
    
    print("worked moving south")
    return True

def test_connectivity():
    """testing"""
    print("testing connectivity")
    
    # Navigate to the sh_commands
    sh_commands_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "sh_commands")
    os.chdir(sh_commands_dir)
    
    # Run shell script to test connectivity
    run_command("./test.sh")
    
    print("Connectivity test over, if no errors printed before, everything working")
    return True

def get_current_path(): # simple helper method for toggling routes
    """finding the current path"""
    success, output = run_command("docker exec -it ha traceroute -n 10.0.15.3", silent=True)
    if success and "10.0.13.3" in output:
        return "south"  # R1-R4-R3 path
    else:
        return "north"  # R1-R2-R3 path

def toggle_path(): # method to toggle the path of the route
    """Toggle path of route"""
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
                       help="call the ospf config script")
    group.add_argument("--host-routes", action="store_true", 
                       help="call the host route config script")
    group.add_argument("--north", action="store_true", 
                       help="Move traffic to the north path (R1->R2->R3)")
    group.add_argument("--south", action="store_true", 
                       help="Move traffic to the south path (R1->R4->R3)")
    group.add_argument("--toggle", action="store_true", 
                       help="Toggle paths")
    group.add_argument("--test", action="store_true", 
                       help="test connectivity")
    group.add_argument("--setup-all", action="store_true", 
                       help="run all setup steps in order")
    
    args = parser.parse_args()
    
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


if __name__ == "__main__":
    main()