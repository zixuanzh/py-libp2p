import json
from pyvis.network import Network
from sys import argv

COLORS = ["#7b47bf", "#70ec84", "#ffa07a", "#005582", "#165042", "#dcb2b8"]

# Read in topology+topics file into map

# Add nodes
def main():
    net = Network()
    net.barnes_hut()

    topology_dict = json.loads(open(argv[1]).read())

    adj_list = topology_dict["topology"]
    topics_map = topology_dict["topic_map"]

    # Assign colors to nodes in topics (note sender is not included in a topic)
    for topic in topics_map:
        index = int(topic)
        color = COLORS[index]
        net.add_nodes(topics_map[topic], \
            color=[color for _ in range(len(topics_map[topic]))])

    nodes_to_add = list(adj_list.keys())
    net.add_nodes(nodes_to_add)
    for node in adj_list:
        node_val = node
        if node != "sender":
            node_val = int(node_val)
        neighbors = adj_list[node]
        for neighbor in neighbors:
            net.add_edge(node_val, neighbor)

    net.show(argv[2])

if __name__ == "__main__":
    main()