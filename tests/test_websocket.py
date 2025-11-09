import asyncio
from unittest.mock import AsyncMock, patch

import pytest
from websockets.exceptions import ConnectionClosedOK
from websockets.frames import Close, CloseCode

from async_websocket_pool.websocket import connect, run_pool


@pytest.mark.asyncio
async def test_connect():
    with patch('websockets.connect') as mock:
        await connect('test_url', on_message=None, on_connect=None)
    mock.assert_called_with('test_url')


@pytest.mark.asyncio
async def test_receive():
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = [None, asyncio.TimeoutError()]

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', on_message=None, on_connect=None, timeout=1)

    mock_websocket.recv.assert_called()


@pytest.mark.asyncio
async def test_on_message_called_with_message():
    mock_message = 'mock_message'
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = [mock_message, asyncio.TimeoutError]
    mock_handler = AsyncMock()

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', on_message=mock_handler, on_connect=None, timeout=1)

    mock_handler.assert_called_with(mock_message)


@pytest.mark.asyncio
async def test_on_connect_called():
    mock_message = 'mock_message'
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = [mock_message, asyncio.TimeoutError]
    mock_on_message = AsyncMock()
    mock_on_connect = AsyncMock()

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect(
            'test_url',
            on_message=mock_on_message,
            on_connect=mock_on_connect,
            timeout=1,
        )

    mock_on_connect.assert_called()


@pytest.mark.asyncio
async def test_timeout(caplog):
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = [None, asyncio.TimeoutError]

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', on_message=lambda x: x, on_connect=None, timeout=5)

    assert "Timeout detected for test_url" in caplog.text


@pytest.mark.asyncio
async def test_connection_closed(caplog):
    mock_websocket = AsyncMock()
    # Build proper close frames for websockets 15.x: supply rcvd, sent, and rcvd_then_sent
    close = Close(CloseCode.NORMAL_CLOSURE, "connection closed")
    mock_websocket.recv.side_effect = ConnectionClosedOK(close, close, True)

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', on_message=lambda x: x, on_connect=None)

    assert "Disconnected from test_url" in caplog.text


@pytest.mark.asyncio
async def test_outer_exception(caplog):
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = Exception('Generic exception thrown.')

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', on_message=lambda x: x, on_connect=None)

    assert 'Generic exception thrown.' in caplog.text


@pytest.mark.asyncio
async def test_reconnect_after_disconnect(caplog):
    # Three sequential connections that immediately close.
    close = Close(CloseCode.NORMAL_CLOSURE, "connection closed")
    mock_websocket1 = AsyncMock()
    mock_websocket1.recv.side_effect = ConnectionClosedOK(close, close, True)
    mock_websocket2 = AsyncMock()
    mock_websocket2.recv.side_effect = ConnectionClosedOK(close, close, True)
    mock_websocket3 = AsyncMock()
    mock_websocket3.recv.side_effect = ConnectionClosedOK(close, close, True)

    async def mock_connect(*args, **kwargs):
        yield mock_websocket1
        yield mock_websocket2
        yield mock_websocket3

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', on_message=lambda x: x, on_connect=None, timeout=5)

    assert caplog.text.count("Disconnected from test_url") == 3


@pytest.mark.asyncio
async def test_run_pool():
    # Create mock async functions
    mock_func1 = AsyncMock()
    mock_func2 = AsyncMock()
    mock_func3 = AsyncMock()
    funcs = [mock_func1, mock_func2, mock_func3]
    await run_pool(funcs)
    mock_func1.assert_called_once()
    mock_func2.assert_called_once()
    mock_func3.assert_called_once()
