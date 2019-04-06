import multiaddr

from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub


TOPIC = "eth"

class ReceiverNode():
    """
    Node which has an internal balance mapping, meant to serve as 
    a dummy crypto blockchain. There is no actual blockchain, just a simple
    map indicating how much crypto each user in the mappings holds
    """

    def __init__(self):
        self.next_msg_id_func = message_id_generator(0)
        self.node_id = str(uuid.uuid1())

    @classmethod
    async def create(cls, sender_node_id):
        """
        Create a new DummyAccountNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = DummyAccountNode()

        libp2p_node = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/0"))

        self.libp2p_node = libp2p_node

        self.floodsub = FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = Pubsub(self.libp2p_node, self.floodsub, "a")

        self.pubsub_messages = await pubsub.subscribe(TOPIC)
        ack_stream = await node.new_stream(sender_node_id, ["/ack/1.0.0"])

        return self

    async def start_receiving():
        # TODO: get peer id
        while True:
            msg = await pubsub_messages.get()
            await ack_stream.write("ack")
