import asyncio
import json 
import multiaddr
import sys
import time
from libp2p.peer.id import ID
from node import Node
from libp2p.peer.peerinfo import info_from_p2p_addr
from tests.utils import cleanup
from Crypto.PublicKey import RSA
from libp2p.peer.id import id_from_public_key

"""
Driver is called in the following way
python receiver_driver.py topology_config.json "my_node_id"
"""

SLEEP_TIME = 5

async def connect(node1, node2_addr):
    # node1 connects to node2
    info = info_from_p2p_addr(node2_addr)
    await node1.connect(info)

async def main():
    # Create Node
    my_transport_opt_str = sys.argv[1]
    node = await Node.create(my_transport_opt_str)

    # Allow for all nodes to start up
    # await asyncio.sleep(SLEEP_TIME)

    if len(sys.argv) == 3:
        neighbor_addr_str = sys.argv[2]

        new_key = RSA.generate(2048, e=65537)
        id_opt = id_from_public_key(new_key.publickey())

        # Add p2p part
        neighbor_addr_str += "/p2p/" + id_opt.pretty()

        # Convert neighbor_addr_str to multiaddr
        neighbor_addr = multiaddr.Multiaddr(neighbor_addr_str)
        print("Connecting")
        await connect(node.libp2p_node, neighbor_addr)
        print("Creating new stream")
        s = await node.libp2p_node.new_stream(id_opt, ["/foo/1"])
        await s.write("foo".encode())
    await asyncio.sleep(15)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    # loop.run_until_complete(main())
    asyncio.ensure_future(main())
    loop.run_forever()
    # loop.close()
