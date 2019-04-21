# py-libp2p [![Build Status](https://travis-ci.com/libp2p/py-libp2p.svg?branch=master)](https://travis-ci.com/libp2p/py-libp2p) [![codecov](https://codecov.io/gh/libp2p/py-libp2p/branch/master/graph/badge.svg)](https://codecov.io/gh/libp2p/py-libp2p) [![Gitter chat](https://badges.gitter.im/gitterHQ/gitter.png)](https://gitter.im/py-libp2p/Lobby)[![Freenode](https://img.shields.io/badge/freenode-%23libp2p-yellow.svg?style=flat-square)](http://webchat.freenode.net/?channels=%23libp2p)



<h1 align="center">
  <img width="250" align="center" src="https://github.com/libp2p/py-libp2p/blob/master/assets/py-libp2p-logo.png?raw=true" alt="py-libp2p hex logo" />
</h1>

## WARNING
py-libp2p is an experimental and work-in-progress repo under heavy development. We do not yet recommend using py-libp2p in production environments.

## Sponsorship
This project is graciously sponsored by the Ethereum Foundation through [Wave 5 of their Grants Program](https://blog.ethereum.org/2019/02/21/ethereum-foundation-grants-program-wave-5/).

## Maintainers
The py-libp2p team consists of:

[@zixuanzh](https://github.com/zixuanzh) [@alexh](https://github.com/alexh) [@stuckinaboot](https://github.com/stuckinaboot) [@robzajac](https://github.com/robzajac)

## Development

py-libp2p requires Python 3.7 and the best way to guarantee a clean Python 3.7 environment is with [`virtualenv`](https://virtualenv.pypa.io/en/stable/)

```sh
virtualenv -p python3.7 venv
. venv/bin/activate
pip3 install -r requirements_dev.txt
python setup.py develop
```

## Testing

After installing our requirements (see above), you can:
```sh
cd tests
pytest
```
Note that tests/libp2p/test_libp2p.py contains an end-to-end messaging test between two libp2p hosts, which is the bulk of our proof of concept.

## Quickstart Guide

This quickstart guide will teach you how to quickly get py-libp2p up and running, and how to take advantage of its various features. Since libp2p at its core is a distributed systems library, this quickstart guide will use explain all concepts with nodes. These two libp2p nodes that are labelled node1 and node2, respectively.

### Creating a libp2p node

A libp2p node, at a high-level, is used for connecting and communicating with peers running libp2p. Connecting with peers implies opening a connection to a peer over which communication via streams (discussed in next section) can take place.

First, we create a libp2p instance on node1 and start listening on port 8000:
```
node1
-----
import multiaddr
from libp2p import new_node

host = await new_node()
await host.get_network().listen(multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/8000"))
```

Then, we create a libp2p instance on node2 and start listening on port 8001
```
node2
-----
import multiaddr
from libp2p import new_node

host = await new_node()
await host.get_network().listen(multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/8001"))
```

Now, we have two libp2p nodes. Next, let's make them connect.

### Connecting two libp2p nodes

In order to connect node1 to node2, node1 must have node2 as a peer. This is so that the nodes know who they are connecting to. So, let's add node2 as a peer of node1 and let's add node1 as a peer of node2. TODO: dicuss p2p IDs

```
node1
-----
from libp2p.peer.peerinfo import info_from_p2p_addr

# Add node2 as a peer of node1
addr_of_node2 = multiaddr.Multiaddr("/ip4/127.0.0.1/tcp/8001/p2p/TODO")
info_node2 = info_from_p2p_addr(addr_of_node2)

# Connect node1 to node2
await node1.connect(info_node2)
```

### Streams between two peers

The central component to the libp2p paradigm is the stream, which represents a channel for communication over an underlying connection. There can be multiple streams over the same underlying connection. Here, we will go over how to setup two nodes to communicate over streams. We refer to the node that initiates the stream (i.e. asks the other node to create a stream) as the initiator and we refer to the node that receives the initiation message as the receiver.

In order for node2 to open a stream to node1, node2 must have node1 as a peer (remember, we only added node2 as a peer of node1 earlier).


### Floodsub between two peers

## Feature Breakdown
py-libp2p aims for conformity with [the standard libp2p modules](https://github.com/libp2p/libp2p/blob/master/REQUIREMENTS.md#libp2p-modules-implementations). Below is a breakdown of the modules we have developed, are developing, and may develop in the future.

> Legend: :green_apple: Done &nbsp; :lemon: In Progress &nbsp; :tomato: Missing &nbsp; :chestnut: Not planned

| libp2p Node                                  | Status        |
| -------------------------------------------- | :-----------: |
| **`libp2p`**                                 | :green_apple: |


| Identify Protocol                            | Status        |
| -------------------------------------------- | :-----------: |
| **`Identify`**                               | :tomato:      |


| Transport Protocols                          | Status        |
| -------------------------------------------- | :-----------: |
| **`TCP`**                                    | :lemon: tests |
| **`UDP`**                                    | :tomato:      |
| **`WebSockets`**                             | :tomato:      |
| **`UTP`**                                    | :tomato:      |
| **`WebRTC`**                                 | :tomato:      |
| **`SCTP`**                                   | :chestnut:    |
| **`Tor`**                                    | :chestnut:    |
| **`i2p`**                                    | :chestnut:    |
| **`cjdns`**                                  | :chestnut:    |
| **`Bluetooth LE`**                           | :chestnut:    |
| **`Audio TP`**                               | :chestnut:    |
| **`Zerotier`**                               | :chestnut:    |
| **`QUIC`**                                   | :chestnut:    |


| Stream Muxers                                | Status        |
| -------------------------------------------- | :-----------: |
| **`multiplex`**                              | :lemon: tests |
| **`yamux`**                                  | :tomato:      |
| **`benchmarks`**                             | :chestnut:    |
| **`muxado`**                                 | :chestnut:    |
| **`spdystream`**                             | :chestnut:    |
| **`spdy`**                                   | :chestnut:    |
| **`http2`**                                  | :chestnut:    |
| **`QUIC`**                                   | :chestnut:    |


| Protocol Muxers                              | Status        |
| -------------------------------------------- | :-----------: |
| **`multiselect`**                            | :green_apple: |


| Switch (Swarm)                               | Status        |
| -------------------------------------------- | :-----------: |
| **`Switch`**                                 | :lemon: tests |
| **`Dialer stack`**                           | :chestnut:    |


| Peer Discovery                               | Status        |
| -------------------------------------------- | :-----------: |
| **`bootstrap list`**                         | :green_apple: |
| **`Kademlia DHT`**                           | :tomato:      |
| **`mDNS`**                                   | :tomato:      |
| **`PEX`**                                    | :chestnut:    |
| **`DNS`**                                    | :chestnut:    |


| Content Routing                              | Status        |
| -------------------------------------------- | :-----------: |
| **`Kademlia DHT`**                           | :tomato:      |
| **`floodsub`**                               | :tomato:      |
| **`gossipsub`**                              | :tomato:      |
| **`PHT`**                                    | :chestnut:    |


| Peer Routing                                 | Status        |
| -------------------------------------------- | :-----------: |
| **`Kademlia DHT`**                           | :tomato:      |
| **`floodsub`**                               | :tomato:      |
| **`gossipsub`**                              | :tomato:      |
| **`PHT`**                                    | :chestnut:    |


| NAT Traversal                                | Status        |
| -------------------------------------------- | :-----------: |
| **`nat-pmp`**                                | :tomato:      |
| **`upnp`**                                   | :tomato:      |
| **`ext addr discovery`**                     | :chestnut:    |
| **`STUN-like`**                              | :chestnut:    |
| **`line-switch relay`**                      | :chestnut:    |
| **`pkt-switch relay`**                       | :chestnut:    |


| Exchange                                     | Status        |
| -------------------------------------------- | :-----------: |
| **`HTTP`**                                   | :chestnut:    |
| **`Bitswap`**                                | :chestnut:    |
| **`Bittorrent`**                             | :chestnut:    |


| Consensus                                    | Status        |
| -------------------------------------------- | :-----------: |
| **`Paxos`**                                  | :chestnut:    |
| **`Raft`**                                   | :chestnut:    |
| **`PBTF`**                                   | :chestnut:    |
| **`Nakamoto`**                               | :chestnut:    |


## Explanation of Basic Two Node Communication

### Core Concepts

_(non-normative, useful for team notes, not a reference)_

Several components of the libp2p stack take part when establishing a connection between two nodes:

1. **Host**: a node in the libp2p network.
2. **Connection**: the layer 3 connection between two nodes in a libp2p network.
3. **Transport**: the component that creates a _Connection_, e.g. TCP, UDP, QUIC, etc.
3. **Streams**: an abstraction on top of a _Connection_ representing parallel conversations about different matters, each of which is identified by a protocol ID. Multiple streams are layered on top of a _Connection_ via the _Multiplexer_.
4. **Multiplexer**: a component that is responsible for wrapping messages sent on a stream with an envelope that identifies the stream they pertain to, normally via an ID. The multiplexer on the other unwraps the message and routes it internally based on the stream identification.
5. **Secure channel**: optionally establishes a secure, encrypted, and authenticated channel over the _Connection_.
5. **Upgrader**: a component that takes a raw layer 3 connection returned by the _Transport_, and performs the security and multiplexing negotiation to set up a secure, multiplexed channel on top of which _Streams_ can be opened.

### Communication between two hosts X and Y

_(non-normative, useful for team notes, not a reference)_

**Initiate the connection**: A host is simply a node in the libp2p network that is able to communicate with other nodes in the network. In order for X and Y to communicate with one another, one of the hosts must initiate the connection.  Let's say that X is going to initiate the connection. X will first open a connection to Y. This connection is where all of the actual communication will take place.

**Communication over one connection with multiple protocols**: X and Y can communicate over the same connection using different protocols and the multiplexer will appropriately route messages for a given protocol to a particular handler function for that protocol, which allows for each host to handle different protocols with separate functions. Furthermore, we can use multiple streams for a given protocol that allow for the same protocol and same underlying connection to be used for communication about separate topics between nodes X and Y.

**Why use multiple streams?**: The purpose of using the same connection for multiple streams to communicate over is to avoid the overhead of having multiple connections between X and Y. In order for X and Y to differentiate between messages on different streams and different protocols, a multiplexer is used to encode the messages when a message will be sent and decode a message when a message is received. The multiplexer encodes the message by adding a header to the beginning of any message to be sent that contains the stream id (along with some other info). Then, the message is sent across the raw connection and the receiving host will use its multiplexer to decode the message, i.e. determine which stream id the message should be routed to.
