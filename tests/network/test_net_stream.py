import asyncio

import pytest

from libp2p.network.stream.exceptions import StreamClosed, StreamEOF, StreamReset
from libp2p.tools.constants import MAX_READ_LEN

DATA = b"data_123"


@pytest.mark.asyncio
async def test_net_stream_read_write(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    assert (
        stream_0.protocol_id is not None
        and stream_0.protocol_id == stream_1.protocol_id
    )
    await stream_0.write(DATA)
    assert (await stream_1.read(MAX_READ_LEN)) == DATA


@pytest.mark.asyncio
async def test_net_stream_read_until_eof(net_stream_pair):
    read_bytes = bytearray()
    stream_0, stream_1 = net_stream_pair

    async def read_until_eof():
        read_bytes.extend(await stream_1.read())

    task = asyncio.ensure_future(read_until_eof())

    expected_data = bytearray()

    # Test: `read` doesn't return before `close` is called.
    await stream_0.write(DATA)
    expected_data.extend(DATA)
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert len(read_bytes) == 0
    # Test: `read` doesn't return before `close` is called.
    await stream_0.write(DATA)
    expected_data.extend(DATA)
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert len(read_bytes) == 0

    # Test: Close the stream, `read` returns, and receive previous sent data.
    await stream_0.close()
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert read_bytes == expected_data

    task.cancel()


@pytest.mark.asyncio
async def test_net_stream_read_after_remote_closed(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_0.write(DATA)
    await stream_0.close()
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert (await stream_1.read(MAX_READ_LEN)) == DATA
    with pytest.raises(StreamEOF):
        await stream_1.read(MAX_READ_LEN)


@pytest.mark.asyncio
async def test_net_stream_read_after_local_reset(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_0.reset()
    with pytest.raises(StreamReset):
        await stream_0.read(MAX_READ_LEN)


@pytest.mark.asyncio
async def test_net_stream_read_after_remote_reset(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_0.write(DATA)
    await stream_0.reset()
    # Sleep to let `stream_1` receive the message.
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    with pytest.raises(StreamReset):
        await stream_1.read(MAX_READ_LEN)


@pytest.mark.asyncio
async def test_net_stream_read_after_remote_closed_and_reset(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_0.write(DATA)
    await stream_0.close()
    await stream_0.reset()
    # Sleep to let `stream_1` receive the message.
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert (await stream_1.read(MAX_READ_LEN)) == DATA


@pytest.mark.asyncio
async def test_net_stream_write_after_local_closed(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_0.write(DATA)
    await stream_0.close()
    with pytest.raises(StreamClosed):
        await stream_0.write(DATA)


@pytest.mark.asyncio
async def test_net_stream_write_after_local_reset(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_0.reset()
    with pytest.raises(StreamClosed):
        await stream_0.write(DATA)


@pytest.mark.asyncio
async def test_net_stream_write_after_remote_reset(net_stream_pair):
    stream_0, stream_1 = net_stream_pair
    await stream_1.reset()
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    with pytest.raises(StreamClosed):
        await stream_0.write(DATA)
