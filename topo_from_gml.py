from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.log import setLogLevel
import networkx as nx
import sys
import os
import time  # Add this import

# ANSI Color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'  # Reset to default color

class ZooTopo(Topo):
    """Mininet topology created from GML file."""
    
    def __init__(self, gml_file=None, **opts):
        """Initialize topology.
        
        Args:
            gml_file: Path to GML file
            **opts: Additional options for Topo
        """
        if gml_file is None:
            raise ValueError("GML file path is required")
        
        # Validate file exists
        if not os.path.exists(gml_file):
            raise FileNotFoundError(f"GML file not found: {gml_file}")
        
        # Validate file is readable
        if not os.access(gml_file, os.R_OK):
            raise PermissionError(f"Cannot read GML file: {gml_file}")
        
        self.gml_file = gml_file
        super(ZooTopo, self).__init__(**opts)
        
        try:
            self._build_topology()
        except Exception as e:
            raise RuntimeError(f"Failed to build topology from {gml_file}: {str(e)}")
    
    def _build_topology(self):
        """Build the topology from GML file."""
        try:
            print(f"{Colors.CYAN}Loading topology from: {self.gml_file}{Colors.END}")
            G = nx.read_gml(self.gml_file)
        except Exception as e:
            raise ValueError(f"Invalid GML file format: {str(e)}")
        
        # Validate graph has nodes
        if len(G.nodes()) == 0:
            raise ValueError("GML file contains no nodes")
        
        node_count = len(G.nodes())
        edge_count = len(G.edges())
        print(f"{Colors.BLUE}Found {node_count} nodes and {edge_count} edges{Colors.END}")
        
        # Create mapping for node names to valid Mininet names
        self.node_mapping = {}
        
        # Add switches for each node
        print(f"{Colors.YELLOW}Creating switches...{Colors.END}")
        for i, node in enumerate(G.nodes()):
            # Create valid switch name (remove spaces and special characters)
            switch_name = f's{i}'
            self.node_mapping[node] = switch_name
            # Add switch, to be managed by DefaultController
            self.addSwitch(switch_name, cls=OVSKernelSwitch) # Removed failMode='standalone'
            print(f"  {switch_name}: {node}")
        
        # Add links for each edge
        print(f"{Colors.YELLOW}Creating links between switches...{Colors.END}")
        for src, dst in G.edges():
            src_switch = self.node_mapping[src]
            dst_switch = self.node_mapping[dst]
            self.addLink(src_switch, dst_switch)
            print(f"  {src_switch} <-> {dst_switch} ({src} <-> {dst})")
        
        # Add a host to each switch
        print(f"{Colors.YELLOW}Creating hosts...{Colors.END}")
        for node in G.nodes():
            switch_name = self.node_mapping[node]
            host_name = switch_name.replace('s', 'h')  # h0, h1, h2, etc.
            self.addHost(host_name)
            self.addLink(host_name, switch_name)
            print(f"  {host_name}: {node}")
        
        print(f"{Colors.GREEN}Topology created successfully:{Colors.END}")
        print(f"  - {node_count} switches")
        print(f"  - {node_count} hosts")
        print(f"  - {edge_count + node_count} links")

    def build(self):
        """Override build method - topology is built in __init__."""
        pass

def main():
    """Main function with enhanced error handling and feedback."""
    setLogLevel('info') # Add this for more verbose Mininet output
    if len(sys.argv) != 2:
        print(f"{Colors.RED}Error: Missing GML file argument{Colors.END}")
        print("Usage: python topo_from_gml.py <topology.gml>")
        print("Example: python topo_from_gml.py Abilene.gml")
        sys.exit(1)
    
    gml_file = sys.argv[1]
    try:
        print(f"{Colors.BOLD}Starting SDN Topology Translator...{Colors.END}")
        print("=" * 50)
        
        # Create topology
        topo = ZooTopo(gml_file=gml_file)
        print("=" * 50)
        print(f"{Colors.MAGENTA}Starting Mininet network...{Colors.END}")
        
        # Using OVSKernelSwitch and explicit DefaultController for L2 learning
        print(f"{Colors.YELLOW}Using OVSKernelSwitch with DefaultController for L2 learning...{Colors.END}")
        net = Mininet(topo=topo, controller=None, switch=OVSKernelSwitch) # Added controller=Controller and switch=OVSKernelSwitch
        net.start()

        print(f"{Colors.CYAN}Network started, waiting 2 seconds for components to initialize...{Colors.END}")
        time.sleep(2) # Wait for 2 seconds

        print(f"{Colors.YELLOW}Disabling STP on all switches...{Colors.END}")
        for switch in net.switches:
            switch.cmd(f'ovs-vsctl set bridge {switch.name} stp_enable=false')
            print(f"  Disabled STP on {switch.name}")
        
        print(f"{Colors.CYAN}STP disabled, waiting 1 second before CLI...{Colors.END}")
        time.sleep(1) # Wait for 1 second

        print(f"{Colors.GREEN}Network setup complete! Ready for CLI.{Colors.END}") # Updated message
        print(f"{Colors.CYAN}Available commands in CLI:{Colors.END}")
        print("   - nodes: Show all nodes")
        print("   - links: Show all links")
        print("   - pingall: Test connectivity")
        print("   - exit: Stop network and exit")
        print("=" * 50)
        
        # Start CLI
        CLI(net)
        
    except FileNotFoundError as e:
        print(f"{Colors.RED}File Error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Tip: Check if the file path is correct and the file exists{Colors.END}")
        sys.exit(1)
        
    except PermissionError as e:
        print(f"{Colors.RED}Permission Error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Tip: Check file permissions or run with appropriate privileges{Colors.END}")
        sys.exit(1)
        
    except ValueError as e:
        print(f"{Colors.RED}Format Error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Tip: Ensure the file is a valid GML format{Colors.END}")
        sys.exit(1)
        
    except RuntimeError as e:
        print(f"{Colors.RED}Runtime Error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Tip: Check the GML file structure and node/edge definitions{Colors.END}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Interrupted by user{Colors.END}")
        
    except Exception as e:
        print(f"{Colors.RED}Unexpected Error: {e}{Colors.END}")
        print(f"{Colors.YELLOW}Tip: Please check the error message and try again{Colors.END}")
        sys.exit(1)
        
    finally:
        # Ensure network cleanup
        try:
            if 'net' in locals():
                print(f"{Colors.CYAN}Stopping network...{Colors.END}")
                net.stop()
                print(f"{Colors.GREEN}Network stopped successfully!{Colors.END}")
        except Exception as cleanup_error:
            print(f"{Colors.YELLOW}Warning during cleanup: {cleanup_error}{Colors.END}")

if __name__ == '__main__':
    main()
