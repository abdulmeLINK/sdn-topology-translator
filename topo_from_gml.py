from mininet.topo import Topo
from mininet.net import Mininet
from mininet.cli import CLI
import networkx as nx

class ZooTopo(Topo):
    def build(self, gml_file):
        G = nx.read_gml(gml_file)
        # Add switches for each node
        for node in G.nodes():
            self.addSwitch(f's{node}')
        # Add links for each edge
        for src, dst in G.edges():
            self.addLink(f's{src}', f's{dst}')
        # Add a host to each switch
        for node in G.nodes():
            self.addHost(f'h{node}')
            self.addLink(f'h{node}', f's{node}')

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        print("Usage: sudo python3 topo_from_gml.py <topology.gml>")
        exit(1)
    gml_file = sys.argv[1]
    topo = ZooTopo(gml_file=gml_file)
    net = Mininet(topo=topo, controller=None)
    net.start()
    CLI(net)
    net.stop()