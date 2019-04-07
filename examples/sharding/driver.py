import asyncio
from sender import SenderNode
from receiver import ReceiverNode
from libp2p.peer.peerinfo import info_from_p2p_addr
from tests.utils import cleanup

ACK_PROTOCOL = "/ack/1.0.0"

async def create_receivers(num_receivers, topic_map):
    receivers = []

    # From topic_map (topic -> list of receivers), create (receiver -> topic)
    receiver_to_topic_map = {}
    for topic in topic_map:
        for receiver in topic_map[topic]:
            receiver_to_topic_map[receiver] = topic

    # Create receivers
    for i in range(num_receivers):
        receivers.append(await ReceiverNode.create(ACK_PROTOCOL, receiver_to_topic_map[i]))
    return receivers

async def connect(node1, node2):
    # node1 connects to node2
    addr = node2.get_addrs()[0]
    info = info_from_p2p_addr(addr)
    await node1.connect(info)

async def create_topology(adjacency_map, sender, receivers):
    # Create network

    # Connect senders to receivers
    for target_num in adjacency_map["sender"]:
        await connect(sender.libp2p_node, receivers[target_num].libp2p_node)

    # Connect receivers to other receivers
    for source_num in adjacency_map:
        if source_num != "sender":
            target_nums = adjacency_map[source_num]
            for target_num in target_nums:
                await connect(receivers[source_num].libp2p_node, \
                    receivers[target_num].libp2p_node)

def get_num_receivers_in_topology(topology):
    receiver_ids = []
    for key in topology:
        if key != "sender":
            if key not in receiver_ids:
                receiver_ids.append(key)
        for neighbor in topology[key]:
            if neighbor not in receiver_ids:
                receiver_ids.append(neighbor)
    return len(receiver_ids)

async def main():
    # Create sender
    print("Sender created")
    sender = await SenderNode.create(ACK_PROTOCOL)

    # Create receivers
    print("Receivers created")

    # Define connection topology
    topology = {
        "sender": [0, 1]
    }

    num_receivers = get_num_receivers_in_topology(topology)
    
    # Define topic map
    topic_map = {
        # "1": [x for x in range(num_receivers)]
        "1": [0],
        "2": [1]
    }

    topics = topic_map.keys()

    receivers = await create_receivers(num_receivers, topic_map)

    # Create network topology
    await create_topology(topology, sender, receivers)
    print("Topology created")

    # Perform throughput test
    # 1) Start receivers 
    sender_info = info_from_p2p_addr(sender.libp2p_node.get_addrs()[0])
    for receiver in receivers:
        print("Starting receiving")
        asyncio.ensure_future(receiver.start_receiving(sender_info))

    # Allow time for start receiving to be completed
    await asyncio.sleep(0.5)

    # 2) Start sending messages and perform throughput test
    # Determine number of receivers in each topic
    num_receivers_in_each_topic = {}
    for topic in topic_map:
        num_receivers_in_each_topic[topic] = len(topic_map[topic])
    print("Performing test")
    await sender.perform_test(num_receivers_in_each_topic, topics, 1)

    await cleanup()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    loop.close()
