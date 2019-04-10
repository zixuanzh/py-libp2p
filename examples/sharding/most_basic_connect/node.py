import asyncio
import multiaddr

from timeit import default_timer as timer

from tests.utils import cleanup
from tests.pubsub.utils import generate_RPC_packet, message_id_generator
from libp2p import new_node
from libp2p.peer.id import ID
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub

SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]
TOPIC = "eth"

class Node():
    def __init__(self):
        pass

    @classmethod
    async def create(cls, transport_opt_str):
        """
        Create a new DummyAccountNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = Node()

        id_opt = ID("peer-")

        print("Sender id: " + id_opt.pretty())
        print("Transport opt is " + transport_opt_str)

        libp2p_node = await new_node(transport_opt=[transport_opt_str])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr(transport_opt_str))

        self.libp2p_node = libp2p_node

        return self