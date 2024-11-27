import matplotlib.pyplot as plt
import networkx as nx

# Define the layers and connections in the neural network based on the description
G = nx.DiGraph()

# Define nodes for inputs, hidden layers (z1, z2, y1, y2), and outputs
nodes = {
    'x1': {'pos': (0, 1)},
    'x2': {'pos': (0, 0)},
    'z1': {'pos': (1, 1.5)},
    'z2': {'pos': (1, -0.5)},
    'y1': {'pos': (2, 1)},
    'y2': {'pos': (2, 0)}
}

# Add nodes to the graph
for node, attr in nodes.items():
    G.add_node(node, pos=attr['pos'])

# Define the edges (connections) based on the mathematical relationships
edges = [
    ('x1', 'z1'),
    ('x2', 'z1'),
    ('x2', 'z2'),
    ('x1', 'z2'),
    ('x1', 'y1'),
    ('x2', 'y1'),
    ('x1', 'y2'),
    ('x2', 'y2'),
    ('z2','y1'),
    ('z1','y2')
]

# Add edges to the graph
G.add_edges_from(edges)

# Get node positions for visualization
pos = nx.get_node_attributes(G, 'pos')

# Draw the network
plt.figure(figsize=(8, 5))
nx.draw(G, pos, with_labels=True, node_size=2000, node_color="lightblue", font_size=10, font_weight='bold', arrows=True)
plt.title("Graph of Neural Network Layers")

plt.show()