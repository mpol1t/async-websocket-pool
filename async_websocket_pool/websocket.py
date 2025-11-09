import asyncio
import inspect
import logging
from asyncio import Semaphore
from typing import Any, Awaitable, Callable, List, Optional

import websockets
from websockets.asyncio.client import ClientConnection
from websockets.exceptions import ConnectionClosed


async def connect(
    url: str,
    on_message: Optional[Callable[[Any], Awaitable[None] | None]],
    on_connect: Optional[Callable[[ClientConnection], Awaitable[None] | None]],
    timeout: Optional[int | float] = None,
    max_concurrent_tasks: int = 10,
    **kwargs: Any,
) -> None:
    """
    Asynchronously connect to a WebSocket endpoint and keep listening until a timeout or
    disconnection occurs, automatically attempting to reconnect.

    This function uses the modern asyncio client in websockets>=15 and the recommended
    reconnection pattern:

        async for websocket in websockets.connect(url, **kwargs):
            ...

    For each established connection:
      - If provided, `on_connect` is invoked once.
      - Incoming messages are read via `recv()` and dispatched to `on_message`.
      - Message handling is executed concurrently, bounded by `max_concurrent_tasks`.
      - If a `timeout` is set, the read loop breaks after an `asyncio.TimeoutError`,
        which triggers a reconnect attempt (next iteration of the async-for).

    Exceptions:
      - `asyncio.TimeoutError` inside the recv loop is handled by logging a warning and
        breaking the inner loop (to reconnect).
      - `websockets.exceptions.ConnectionClosed` (covers both OK and error closes) is
        handled by logging a warning and allowing the outer loop to reconnect.
      - Any other exception is logged and then the outer loop continues (reconnect).

    Notes for websockets 15.0.1:
      - Use `websockets.asyncio.client.ClientConnection` for type hints (replaces the
        deprecated `WebSocketClientProtocol`).
      - `websockets.connect(...)` at the top level now aliases the modern asyncio client.

    Args:
        url: The WebSocket URL to connect to.
        on_message: Callback invoked for each received message. May be sync or async.
        on_connect: Callback invoked after a connection is established. May be sync or async.
        timeout: Optional seconds to wait for a message before reconnecting. If None, wait
        indefinitely. max_concurrent_tasks: Maximum number of message handler tasks running
        at once. **kwargs: Additional keyword arguments forwarded to `websockets.connect`.

    Returns:
        None
    """

    semaphore: Semaphore = Semaphore(max_concurrent_tasks)

    async def _run_handler(handler: Optional[Callable[..., Any]], *args: Any) -> None:
        """Run a sync or async handler safely without crashing the recv loop."""
        if handler is None:
            return
        try:
            result = handler(*args)
            if inspect.isawaitable(result):
                await result
        except Exception:
            logging.exception("Exception in handler")

    async def _handle_message(msg: Any) -> None:
        async with semaphore:
            await _run_handler(on_message, msg)

    # Top-level websockets.connect is compatible with v15 and remains patchable in tests.
    async for websocket in websockets.connect(url, **kwargs):
        try:
            logging.info(f"Connected to {url}")

            # Inform client code about a fresh connection (sync or async).
            await _run_handler(on_connect, websocket)

            # Receive loop for this connection.
            while True:
                try:
                    message: Any = await asyncio.wait_for(websocket.recv(), timeout=timeout)
                    # Process messages concurrently (bounded by semaphore).
                    asyncio.create_task(_handle_message(message))
                except asyncio.TimeoutError:
                    logging.warning(f"Timeout detected for {url}")
                    # Break to trigger reconnection via the async-for.
                    break

        except ConnectionClosed:
            logging.warning(f"Disconnected from {url}")
        except Exception:
            # Log unexpected exceptions and proceed to the next reconnect attempt.
            logging.exception("Unexpected exception in websocket loop")


async def run_pool(funcs: List[Callable[[], Awaitable[None]]]) -> None:
    """
    Concurrently execute a list of asynchronous, parameterless callables using asyncio.gather.

    This helper is useful for running multiple websocket client coroutines or related tasks
    in parallel.

    Args:
        funcs: A list of async, parameterless callables (coroutines) to run concurrently.

    Raises:
        Propagates the first exception raised among the provided coroutines.

    Returns:
        None
    """
    await asyncio.gather(*(f() for f in funcs))
