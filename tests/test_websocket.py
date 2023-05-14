import asyncio
from unittest.mock import patch, Mock, AsyncMock

import pytest
import websockets

from async_websocket_pool.websocket import connect
from async_websocket_pool.websocket import run_pool


@pytest.mark.asyncio
async def test_connect():
    with patch('websockets.connect') as mock:
        await connect('test_url', message_handler=None)

    mock.assert_called_with('test_url')


@pytest.mark.asyncio
async def test_receive():
    mock_websocket = AsyncMock()

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', message_handler=None, timeout=1)

    mock_websocket.recv.assert_called()


@pytest.mark.asyncio
async def test_handler_called_with_message():
    mock_message = 'mock_message'
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = [mock_message, asyncio.TimeoutError]
    mock_handler = Mock()

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', message_handler=mock_handler, timeout=1)

    mock_handler.assert_called_with(mock_message)


@pytest.mark.asyncio
async def test_timeout(caplog):
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = [None, asyncio.TimeoutError]

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', message_handler=lambda x: x, timeout=5)

    assert "Timeout detected for test_url" in caplog.text


@pytest.mark.asyncio
async def test_connection_closed(caplog):
    mock_websocket = AsyncMock()
    mock_websocket.recv.side_effect = websockets.ConnectionClosed(1000, 'connection closed')

    async def mock_connect(*args, **kwargs):
        yield mock_websocket

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', message_handler=lambda x: x)

    assert "Disconnected from test_url" in caplog.text


@pytest.mark.asyncio
async def test_reconnect_after_disconnect(caplog):
    mock_websocket1 = AsyncMock()
    mock_websocket1.recv.side_effect = websockets.ConnectionClosed(1000, 'connection closed')
    mock_websocket2 = AsyncMock()
    mock_websocket2.recv.side_effect = websockets.ConnectionClosed(1000, 'connection closed')
    mock_websocket3 = AsyncMock()
    mock_websocket3.recv.side_effect = websockets.ConnectionClosed(1000, 'connection closed')

    async def mock_connect(*args, **kwargs):
        yield mock_websocket1
        yield mock_websocket2
        yield mock_websocket3

    with patch('websockets.connect', new=mock_connect):
        await connect('test_url', message_handler=lambda x: x, timeout=5)

    assert caplog.text.count("Disconnected from test_url") == 3


@pytest.mark.asyncio
async def test_run_pool():
    # Create mock async functions
    mock_func1 = AsyncMock()
    mock_func2 = AsyncMock()
    mock_func3 = AsyncMock()

    funcs = [mock_func1, mock_func2, mock_func3]

    # Run the mock functions in a pool
    await run_pool(funcs)

    # Check that each mock function was called
    mock_func1.assert_called_once()
    mock_func2.assert_called_once()
    mock_func3.assert_called_once()
