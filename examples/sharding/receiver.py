import multiaddr

from libp2p import new_node
from libp2p.pubsub.pubsub import Pubsub
from libp2p.pubsub.floodsub import FloodSub


TOPIC = "eth"


def main():
    node = await new_node(transport_opt=["TODO"])
    await node.get_network().listen(multiaddr.Multiaddr("TODO"))

    floodsub = FloodSub(["/floodsub/1.0.0"])
    pubsub = Pubsub(node, floodsub, "unnecessary-id")

    pubsub_messages = await pubsub.subscribe(TOPIC)

    # TODO: get peer id
    ack_stream = await node.new_stream("TODO", ["/ack/1"])

    while True:
        msg = await pubsub_messages.get()
        await ack_stream.write("ack")


if __name__ == '__main__':
    main()
