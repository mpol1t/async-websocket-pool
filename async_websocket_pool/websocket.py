import asyncio
import logging
import sys
from typing import Any, Optional, Callable, List

import websockets
from websockets import WebSocketClientProtocol

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))


async def connect(
        url: str,
        on_message: Callable[[Any], None],
        on_connect: Optional[Callable[[WebSocketClientProtocol], None]],
        timeout: Optional[int | float] = None,
        **kwargs
) -> None:
    """
    Asynchronously establishes a WebSocket connection to a given endpoint and continuously listens
    for incoming messages until a timeout or a disconnection occurs.

    This function initiates a connection to a specified WebSocket URL and invokes the provided
    message handler function for every message received. In case of a disconnection, it attempts
    to reestablish the connection using an exponential backoff strategy.

    The timeout parameter controls how long the function will wait for a message before the
    receive operation expires. If the timeout is set to None, the function will wait indefinitely
    for a message. If a timeout duration is specified, the function will wait for that period before
    timing out and attempting to reconnect.

    All exceptions, except for asyncio.TimeoutError and websockets.ConnectionClosed, are logged and
    propagated up the call stack.

    :param url: The WebSocket URL to establish the connection.
    :param on_message: A callback function to handle incoming messages. This function should
                            accept a single argument which will be the received message.
    :param on_connect: A callback function that is executed every time successful connection is established.
    :param timeout: Optional; The maximum wait time for a message, in seconds. If set to None,
                    the function will wait indefinitely for a message.
    :param kwargs: Optional; Additional keyword arguments for the websockets.connect function to
                   further customize the WebSocket connection.
    :return: None

    :raises: This function propagates all exceptions except for asyncio.TimeoutError and
             websockets.ConnectionClosed, which are handled internally.
    """
    async for websocket in websockets.connect(url, **kwargs):
        try:
            logger.info(f'Connected to {url}')

            if on_connect:
                on_connect(websocket)

            while True:
                try:
                    message: Any = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    on_message(message)
                except asyncio.TimeoutError:
                    logger.warning(f'Timeout detected for {url}')
                    break
        except websockets.ConnectionClosed:
            logger.warning(f'Disconnected from {url}')
        except Exception as e:
            logger.exception(e)


async def run_pool(funcs: List[Callable]) -> None:
    """
    Concurrently executes a list of asynchronous functions utilizing the asyncio.gather method.

    This function serves as a utility for managing concurrent execution of tasks, effectively
    creating an asynchronous "pool" of functions. By leveraging Python's asyncio library, it
    initiates all provided coroutine functions concurrently, thereby improving efficiency
    when dealing with multiple IO-bound tasks.

    Note: This function does not guarantee any specific order of execution or completion
    of the provided functions. If such an order is necessary, consider managing dependencies
    within your asynchronous routines themselves.

    :param funcs: A list of asynchronous, parameterless Callable objects (coroutine functions)
                  that are to be executed concurrently. Each function in the list should be
                  defined with the async keyword and should not require any arguments.

    :raises: This function will propagate any exceptions raised by the asyncio.gather method
             which in turn raises the first exception that gets raised amongst the provided
             coroutine functions.

    :return: None
    """
    await asyncio.gather(*(f() for f in funcs))
