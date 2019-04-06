import asyncio
import multiaddr

from timeit import default_timer as timer

from tests.pubsub.utils import generate_RPC_packet, message_id_generator
from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub

SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]
TOPIC = "eth"

class SenderNode():
    """
    Node which has an internal balance mapping, meant to serve as 
    a dummy crypto blockchain. There is no actual blockchain, just a simple
    map indicating how much crypto each user in the mappings holds
    """

    def __init__(self):
        self.next_msg_id_func = message_id_generator(0)
        self.ack_queue = asyncio.Queue()

    @classmethod
    async def create(cls, ack_protocol):
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
        await self.pubsub.subscribe(TOPIC)

        self.test_being_performed = True

        this = self

        async def ack_stream_handler(stream):
            while self.test_being_performed:
                ack = await stream.read()
                if ack is not None:
                    await self.ack_queue.put(ack)

            # Reached once test_being_performed is False
            # Notify receivers test is over
            await stream.write("end".encode())
        # Set handler for acks
        self.ack_protocol = ack_protocol
        self.libp2p_node.set_stream_handler(self.ack_protocol, ack_stream_handler)

        return self

    async def perform_test(self, num_receivers, topics, time_length):
        # Time and loop
        start = timer()
        curr_time = timer()

        my_id = str(self.libp2p_node.get_id())
        msg_contents = "transaction"

        num_sent = 0
        num_fully_ack = 0
        while (curr_time - start) < time_length:
            # Send message (NOTE THIS IS JUST ONE TOPIC)
            packet = generate_RPC_packet(my_id, topics, msg_contents, self.next_msg_id_func())
            await self.floodsub.publish(my_id, packet.SerializeToString())
            num_sent += 1
            # Wait for acks
            num_acks = 0
            while num_acks < num_receivers:
                await self.ack_queue.get()
                num_acks += 1
            num_fully_ack += 1
            curr_time = timer()

        # Do something interesting with test results
        print("Num sent: " + str(num_sent))
        print("Num fully ack: " + str(num_fully_ack))
        
        # End test
        self.test_being_performed = False
