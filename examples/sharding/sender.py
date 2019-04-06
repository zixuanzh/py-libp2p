import asyncio
import multiaddr

from timeit import default_timer as timer

from tests.pubsub.utils import generate_RPC_packet, message_id_generator
from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub


TOPIC = "eth"
NUM_RECEIVERS = 10
TIME_LENGTH = 1000 # seconds, double check
ack_queue = asyncio.Queue()


def main():
    node = await new_node(transport_opt=["TODO"])
    await node.get_network().listen(multiaddr.Multiaddr("TODO"))

    floodsub = FloodSub(["/floodsub/1.0.0"])
    pubsub = Pubsub(node, floodsub, "unnecessary-id")

    next_msg_id_func = message_id_generator(0)

    """
    if is_sharded:
        # Subscribe to certain topics
        # TODO
        pass
    else:
        # Subscribe to just one topic
        await pubsub.subscribe(TOPIC)
    """

    await pubsub.subscribe(TOPIC)

    async def ack_stream_handler(stream):
        while True:
            ack = await stream.read()

            if ack is not None:
                await ack_queue.put(ack)

    # Set handler for acks
    node.set_stream_handler("/ack/1", ack_stream_handler)

    # Time and loop
    start = timer()
    curr_time = timer()

    while (curr_time - start) < TIME_LENGTH:
        # Send message (NOTE THIS IS JUST ONE TOPIC)
        my_id = str(node.get_id())
        msg_contents = "transaction"
        packet = generate_RPC_packet(my_id, [TOPIC], msg_contents, next_msg_id_func())
        await floodsub.publish(my_id, packet.SerializeToString())

        # Wait for acks
        num_acks = 0
        while num_acks < NUM_RECEIVERS:
            await ack_queue.get()
            num_acks += 1

        curr_time = timer()


if __name__ == '__main__':
    main()
