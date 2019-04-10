import asyncio
import json 
import multiaddr
import sys
import time
from libp2p.peer.id import ID
from sender import SenderNode
from receiver import ReceiverNode
from libp2p.peer.peerinfo import info_from_p2p_addr
from tests.utils import cleanup

SLEEP_TIME = 5

async def connect(node1, node2_addr):
    # node1 connects to node2
    info = info_from_p2p_addr(node2_addr)
    await node1.connect(info)

async def main():
    """
    Read in topology config file, which contains
    a map of node IDs to peer IDs, an adjacency list (named topology) using node IDs,
    a map of node IDs to topics, and ACK_PROTOCOL
    """
    topology_config_dict = json.loads(open(sys.argv[1]).read())
    my_node_id = sys.argv[2]

    ack_protocol = topology_config_dict["ACK_PROTOCOL"]

    # Create sender
    print("Creating sender")
    my_transport_opt_str = topology_config_dict["node_id_map"][my_node_id]
    sender_node = await SenderNode.create(my_node_id, my_transport_opt_str, ack_protocol)
    print("Sender created")

    # Allow for all nodes to start up
    # await asyncio.sleep(SLEEP_TIME)

    return

    new_key = RSA.generate(2048, e=65537)
    id_opt = id_from_public_key(new_key.publickey())

    # Connect sender node to all other relevant sender nodes
    for neighbor in topology_config_dict["topology"][my_node_id]:
        neighbor_addr_str = topology_config_dict["node_id_map"][neighbor]

        # Add p2p part
        neighbor_addr_str += "/p2p/" + id_opt.pretty()

        # Convert neighbor_addr_str to multiaddr
        neighbor_addr = multiaddr.Multiaddr(neighbor_addr_str)
        await connect(sender_node.libp2p_node, neighbor_addr)

    # Perform throughput test
    # Start sending messages and perform throughput test
    # Determine number of receivers in each topic
    topic_map = topology_config_dict["topic_map"]
    topics = topic_map.keys()

    num_receivers_in_each_topic = {}
    for topic in topic_map:
        num_receivers_in_each_topic[topic] = len(topic_map[topic])
    print("Performing test")
    await sender_node.perform_test(num_receivers_in_each_topic, topics, 10)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()