import asyncio
import multiaddr

from tests.pubsub.utils import message_id_generator, generate_RPC_packet
from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub
from ordered_queue import OrderedQueue

SUPPORTED_PUBSUB_PROTOCOLS = ["/floodsub/1.0.0"]
BEE_MOVIE_TOPIC = "bee_movie"


class MsgOrderingNode():

    def __init__(self):
        self.balances = {}
        self.next_msg_id_func = message_id_generator(0)
        self.priority_queue = OrderedQueue()
        # self.last_word_gotten_seqno = 0

    @classmethod
    async def create(cls):
        """
        Create a new DummyAccountNode and attach a libp2p node, a floodsub, and a pubsub
        instance to this new node

        We use create as this serves as a factory function and allows us
        to use async await, unlike the init function
        """
        self = MsgOrderingNode()

        libp2p_node = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/0"])
        await libp2p_node.get_network().listen(multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/0"))

        self.libp2p_node = libp2p_node

        self.floodsub = FloodSub(SUPPORTED_PUBSUB_PROTOCOLS)
        self.pubsub = Pubsub(self.libp2p_node, self.floodsub, "a")
        return self

    async def handle_incoming_msgs(self):
        """
        Handle all incoming messages on the BEE_MOVIE_TOPIC from peers
        """
        while True:
            incoming = await self.q.get()  
            seqno = int.from_bytes(incoming.seqno, byteorder='big')
            word = incoming.data.decode('utf-8')

            await self.handle_bee_movie_word(seqno, word)

    async def setup_crypto_networking(self):
        """
        Subscribe to BEE_MOVIE_TOPIC and perform call to function that handles
        all incoming messages on said topic
        """
        self.q = await self.pubsub.subscribe(BEE_MOVIE_TOPIC)

        asyncio.ensure_future(self.handle_incoming_msgs())

    async def publish_bee_movie_word(self, word, msg_id=None):
        my_id = str(self.libp2p_node.get_id())
        if msg_id is None:
            msg_id = self.next_msg_id_func()
        packet = generate_RPC_packet(my_id, [BEE_MOVIE_TOPIC], word, msg_id)
        await self.floodsub.publish(my_id, packet.SerializeToString())

    async def handle_bee_movie_word(self, seqno, word):
        # print("Handle hit for " + str(seqno) + ", " + word)
        await self.priority_queue.put((seqno, word))

    async def get_next_word_in_bee_movie(self):
        # Get just the word (and not the seqno) and return the word
        next_word = (await self.priority_queue.get())[1]
        return next_word
