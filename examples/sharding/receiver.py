import multiaddr
import asyncio

from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub
from tests.pubsub.utils import message_id_generator

TOPIC = "eth"
SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]

class ReceiverNode():
    """
    Node which has an internal balance mapping, meant to serve as 
    a dummy crypto blockchain. There is no actual blockchain, just a simple
    map indicating how much crypto each user in the mappings holds
    """

    def __init__(self):
        self.next_msg_id_func = message_id_generator(0)

    @classmethod
    async def create(cls, ack_protocol, topic):
        """
        Create a new ReceiverNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = ReceiverNode()

        libp2p_node = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/0"))

        self.libp2p_node = libp2p_node

        self.floodsub = FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = Pubsub(self.libp2p_node, self.floodsub, "a")

        self.pubsub_messages = await self.pubsub.subscribe(topic)
        self.topic = topic

        self.ack_protocol = ack_protocol

        return self

    async def wait_for_end(self, ack_stream):
        # Continue waiting for end message, even if None (i.e. timeout) is received
        msg = await ack_stream.read()
        while msg is None:
            msg = await ack_stream.read()
        msg = msg.decode()
        if msg == "end":
            self.should_listen = False
            print("End received")

    async def start_receiving(self, sender_node_info):
        await self.libp2p_node.connect(sender_node_info)
        ack_stream = await self.libp2p_node.new_stream(sender_node_info.peer_id, [self.ack_protocol])
        asyncio.ensure_future(self.wait_for_end(ack_stream))

        self.should_listen = True
        ack_msg = self.topic
        encoded_ack_msg = ack_msg.encode()
        while self.should_listen:
            msg = await self.pubsub_messages.get()
            await ack_stream.write(encoded_ack_msg)
        print("Receiver closed")
