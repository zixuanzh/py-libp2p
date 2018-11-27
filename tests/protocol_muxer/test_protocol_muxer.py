import pytest

from libp2p.libp2p import new_node
from protocol_muxer.multiselect_client import MultiselectClientError

async def perform_simple_test(protocols_for_client, protocols_with_handlers):
    node_a = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/8001/ipfs/node_a"])
    node_b = await new_node(transport_opt=["/ip4/127.0.0.1/tcp/8000/ipfs/node_b"])

    async def stream_handler(stream):
        while True:
            read_string = (await stream.read()).decode()
            print("host B received:" + read_string)

            response = "ack:" + read_string
            print("sending response:" + response)
            await stream.write(response.encode())

    for protocol in protocols_with_handlers:
        node_b.set_stream_handler(protocol, stream_handler)

    # Associate the peer with local ip address (see default parameters of Libp2p())
    node_a.get_peerstore().add_addr("node_b", "/ip4/127.0.0.1/tcp/8000", 10)

    stream = await node_a.new_stream("node_b", protocols_for_client)
    messages = ["hello" + str(x) for x in range(10)]
    for message in messages:
        await stream.write(message.encode())

        response = (await stream.read()).decode()

        print("res: " + response)
        assert response == ("ack:" + message)

    # Success, terminate pending tasks.
    return

@pytest.mark.asyncio
async def test_single_protocol_succeeds():
    await perform_simple_test(["/echo/1.0.0"], ["/echo/1.0.0"])

@pytest.mark.asyncio
async def test_single_protocol_fails():
    with pytest.raises(MultiselectClientError) as e_info:
        await perform_simple_test(["/echo/1.0.0"], ["/potato/1.0.0"])

@pytest.mark.asyncio
async def test_multiple_protocol_first_is_valid_succeeds():
    protocols_for_client = ["/echo/1.0.0", "/potato/1.0.0"]
    protocols_for_listener = ["/foo/1.0.0", "/echo/1.0.0"]
    await perform_simple_test(protocols_for_client, protocols_for_listener)

@pytest.mark.asyncio
async def test_multiple_protocol_second_is_valid_succeeds():
    protocols_for_client = ["/rock/1.0.0", "/foo/1.0.0"]
    protocols_for_listener = ["/foo/1.0.0", "/echo/1.0.0"]
    await perform_simple_test(protocols_for_client, protocols_for_listener)

@pytest.mark.asyncio
async def test_multiple_protocol_fails():
    protocols_for_client = ["/rock/1.0.0", "/foo/1.0.0", "/bar/1.0.0"]
    protocols_for_listener = ["/aspyn/1.0.0", "/rob/1.0.0", "/zx/1.0.0", "/alex/1.0.0"]
    with pytest.raises(MultiselectClientError) as e_info:
        await perform_simple_test(protocols_for_client, protocols_for_listener)
