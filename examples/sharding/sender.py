import asyncio
import multiaddr

from timeit import default_timer as timer

from tests.utils import cleanup
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
                print("WAITING ON READ")
                ack = await stream.read()
                print("READ OCC")
                if ack is not None:
                    await self.ack_queue.put(ack)

            # Reached once test_being_performed is False
            # Notify receivers test is over
            print("TEST STOPPED BEING PERFORMED")
            await stream.write("end".encode())
        # Set handler for acks
        self.ack_protocol = ack_protocol
        self.libp2p_node.set_stream_handler(self.ack_protocol, ack_stream_handler)

        return self

    async def perform_test(self, num_receivers_in_each_topic, topics, time_length):
        # Time and loop
        # start = timer()
        # curr_time = timer()

        my_id = str(self.libp2p_node.get_id())
        msg_contents = "transaction"

        num_sent_in_each_topic = {}
        num_acks_in_each_topic = {}
        for topic in topics:
            num_sent_in_each_topic[topic] = 0
            num_acks_in_each_topic[topic] = 0

        self.topic_ack_queues = {}
        for topic in topics:
            self.topic_ack_queues[topic] = asyncio.Queue()

        async def handle_ack_queues():
            start = timer()
            curr_time = timer()
            while (curr_time - start) < time_length:
                # print("GETTING ACK")
                ack = await self.ack_queue.get()
                # print("DECODING ACK")
                decoded_ack = ack.decode()

                # print("ACK REC IN HANDLE")
                await self.topic_ack_queues[decoded_ack].put(decoded_ack)
                # print("ADDING TO TOPIC ACK QUEUE " + str(topic))
                curr_time = timer()
            print("EXI HANDLE ACK QUES")
            self.test_being_performed = False

        gathered = None

        async def perform_test_on_topic(topic):
            print("Performing test on topic " + topic)
            start = timer()
            curr_time = timer()
            # Perform test while time is not up here AND
            # while time is not up in handle_ack_queues, which is checked with the
            # self.test_being_performed boolean
            while (curr_time - start) < time_length and self.test_being_performed:
                # Send message (NOTE THIS IS JUST ONE TOPIC)
                packet = generate_RPC_packet(my_id, [topic], msg_contents, self.next_msg_id_func())
                # print("PUBLISHED")
                await self.floodsub.publish(my_id, packet.SerializeToString())
                num_sent_in_each_topic[topic] += 1
                
                # Wait for acks
                num_acks = 0
                # print("PRE WHILE")

                # While number of acks is below threshold AND
                # while time is not up in handle_ack_queues, which is checked with the
                # self.test_being_performed boolean 
                # TODO: Check safety of this. Does this make sense in the asyncio
                # event-driven setting?
                while num_acks < num_receivers_in_each_topic[topic] and self.test_being_performed:
                    # print("IN WHILE")
                    await self.topic_ack_queues[topic].get()
                    # print("GOT")
                    num_acks += 1
                num_acks_in_each_topic[topic] += 1
                curr_time = timer()
            self.test_being_performed = False
            print("Time passed")
            print("CANCELING")
            # await cleanup()

        tasks = [asyncio.ensure_future(handle_ack_queues())]

        for topic in topics:
            tasks.append(asyncio.ensure_future(perform_test_on_topic(topic)))

        gathered = await asyncio.gather(*tasks, return_exceptions=True)
        # while (curr_time - start) < time_length:
        #     # Send message (NOTE THIS IS JUST ONE TOPIC)
        #     packet = generate_RPC_packet(my_id, topics, msg_contents, self.next_msg_id_func())
        #     await self.floodsub.publish(my_id, packet.SerializeToString())
        #     num_sent += 1
        #     # Wait for acks
        #     num_acks = 0
        #     while num_acks < num_receivers:
        #         await self.ack_queue.get()
        #         num_acks += 1
        #     num_fully_ack += 1
        #     curr_time = timer()

        # Do something interesting with test results
        print("Num sent: " + str(num_sent_in_each_topic))
        print("Num fully ack: " + str(num_acks_in_each_topic))
        
        # End test
        self.test_being_performed = False
