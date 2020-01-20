import asyncio

import pytest


@pytest.mark.asyncio
async def test_mplex_conn(mplex_conn_pair):
    conn_0, conn_1 = mplex_conn_pair

    assert len(conn_0.streams) == 0
    assert len(conn_1.streams) == 0
    assert not conn_0.event_shutting_down.is_set()
    assert not conn_1.event_shutting_down.is_set()
    assert not conn_0.event_closed.is_set()
    assert not conn_1.event_closed.is_set()

    # Test: Open a stream, and both side get 1 more stream.
    stream_0 = await conn_0.open_stream()
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert len(conn_0.streams) == 1
    assert len(conn_1.streams) == 1
    # Test: From another side.
    stream_1 = await conn_1.open_stream()
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    assert len(conn_0.streams) == 2
    assert len(conn_1.streams) == 2

    # Close from one side.
    await conn_0.close()
    # Sleep for a while for both side to handle `close`.
    await asyncio.sleep(0.01)  # todo: remove sleep or justify existence
    # Test: Both side is closed.
    assert conn_0.event_shutting_down.is_set()
    assert conn_0.event_closed.is_set()
    assert conn_1.event_shutting_down.is_set()
    assert conn_1.event_closed.is_set()
    # Test: All streams should have been closed.
    assert stream_0.event_remote_closed.is_set()
    assert stream_0.event_reset.is_set()
    assert stream_0.event_local_closed.is_set()
    assert conn_0.streams is None
    # Test: All streams on the other side are also closed.
    assert stream_1.event_remote_closed.is_set()
    assert stream_1.event_reset.is_set()
    assert stream_1.event_local_closed.is_set()
    assert conn_1.streams is None

    # Test: No effect to close more than once between two side.
    await conn_0.close()
    await conn_1.close()
