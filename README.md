# SDN Topology Translator

Convert GML files to Mininet topologies for SDN simulation.

## Overview

A simple tool that translates network topology files from GML (Graph Modeling Language) format into Mininet topologies for Software-Defined Networking research and testing.

## Features

- Convert GML files to Mininet topologies
- Automatic host and switch generation
- Error handling and validation
- Simple command-line interface

## Installation

```powershell
# Install dependencies
pip install networkx mininet
```

## Usage

### Command Line

```powershell
# Basic usage
python topo_from_gml.py topology.gml

# Example with provided file
python topo_from_gml.py Abilene.gml
```

### Python API

```python
from topo_from_gml import ZooTopo
from mininet.net import Mininet
from mininet.cli import CLI

# Create topology and network
topo = ZooTopo(gml_file="topology.gml")
net = Mininet(topo=topo, controller=None)
net.start()
CLI(net)
net.stop()
```

## How It Works

1. Reads GML file using NetworkX
2. Creates a switch for each node in the graph
3. Creates links between switches based on graph edges
4. Adds one host to each switch
5. Launches Mininet CLI for interaction

## Requirements

- Python 3.x
- NetworkX library
- Mininet framework
- Valid GML topology file

## Error Handling

The tool includes validation for:
- File existence and readability
- Valid GML format
- Network creation errors
- Proper cleanup on exit

## Troubleshooting

### Common Issues

**File not found error:**
- Check if the GML file path is correct
- Ensure the file exists in the specified location

**Permission error:**
- Check file read permissions
- Run with appropriate privileges if needed

**Invalid GML format:**
- Verify the GML file is properly formatted
- Check for syntax errors in the GML file

**Network startup issues:**
- Ensure Mininet is properly installed
- Check if you have sufficient privileges to create network interfaces

### Support

For issues and questions, please check:
1. File permissions and paths
2. GML file format validity
3. Mininet installation and requirements
