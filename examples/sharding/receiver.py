import multiaddr
import asyncio

from libp2p import new_node
from libp2p.peer.peerinfo import info_from_p2p_addr
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub
from tests.pubsub.utils import message_id_generator
from libp2p.peer.id import ID

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
    async def create(cls, node_id, transport_opt_str, ack_protocol, topic):
        """
        Create a new ReceiverNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = ReceiverNode()

        id_opt = ID("peer-" + node_id)

        libp2p_node = await new_node(transport_opt=[transport_opt_str])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr(transport_opt_str))

        self.libp2p_node = libp2p_node

        self.floodsub = None #FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = None #Pubsub(self.libp2p_node, self.floodsub, "a")

        self.pubsub_messages = None #await self.pubsub.subscribe(topic)
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
        print("Receiving started")

        await self.libp2p_node.connect(sender_node_info)

        print("Connection to sender confirmed")
        print("Creating ack stream with ack protocol " + self.ack_protocol \
            + ", peer_id " + sender_node_info.peer_id.pretty())

        ack_stream = await self.libp2p_node.new_stream(sender_node_info.peer_id, [self.ack_protocol])
        print("Ack stream created")
        asyncio.ensure_future(self.wait_for_end(ack_stream))

        print("Listening for ack messages")
        self.should_listen = True
        ack_msg = self.topic
        encoded_ack_msg = ack_msg.encode()
        while self.should_listen:
            msg = await self.pubsub_messages.get()
            await ack_stream.write(encoded_ack_msg)
        print("Receiver closed")
