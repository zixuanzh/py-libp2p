import asyncio
import multiaddr

from timeit import default_timer as timer

from tests.pubsub.utils import generate_RPC_packet, message_id_generator
from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub

SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]
TOPIC = "eth"
NUM_RECEIVERS = 10
TIME_LENGTH = 1000 # seconds, double check

class SenderNode():
    """
    Node which has an internal balance mapping, meant to serve as 
    a dummy crypto blockchain. There is no actual blockchain, just a simple
    map indicating how much crypto each user in the mappings holds
    """

    def __init__(self):
        self.next_msg_id_func = message_id_generator(0)
        self.node_id = str(uuid.uuid1())
        self.ack_queue = asyncio.Queue()

    @classmethod
    async def create(cls):
        """
        Create a new DummyAccountNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = SenderNode()

        libp2p_node = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/0"))

        self.libp2p_node = libp2p_node

        self.floodsub = FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = Pubsub(self.libp2p_node, self.floodsub, "a")
        await pubsub.subscribe(TOPIC)

        async def ack_stream_handler(stream):
            while True:
                ack = await stream.read()

                if ack is not None:
                    await ack_queue.put(ack)

        # Set handler for acks
        self.libp2p_node.set_stream_handler("/ack/1", ack_stream_handler)

        return self

    def perform_test():
        # Time and loop
        start = timer()
        curr_time = timer()

        my_id = str(self.libp2p_node.get_id())
        msg_contents = "transaction"

        while (curr_time - start) < TIME_LENGTH:
            # Send message (NOTE THIS IS JUST ONE TOPIC)
            packet = generate_RPC_packet(my_id, [TOPIC], msg_contents, self.next_msg_id_func())
            await floodsub.publish(my_id, packet.SerializeToString())

            # Wait for acks
            num_acks = 0
            while num_acks < NUM_RECEIVERS:
                await self.ack_queue.get()
                num_acks += 1

        curr_time = timer()
