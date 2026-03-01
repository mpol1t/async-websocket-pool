[![codecov](https://codecov.io/gh/mpol1t/async-websocket-pool/branch/main/graph/badge.svg?token=IXD2CSFA1N)](https://codecov.io/gh/mpol1t/async-websocket-pool)
![GitHub](https://img.shields.io/github/license/mpol1t/async-websocket-pool)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/async-websocket-pool)
[![CodeQL](https://github.com/mpol1t/async-websocket-pool/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/mpol1t/async-websocket-pool/actions/workflows/github-code-scanning/codeql)
![PyPI - Version](https://img.shields.io/pypi/v/async-websocket-pool)
# Async WebSocket Pool

This repository contains a Python-based asynchronous WebSocket pool that allows for asynchronous connections to multiple WebSocket endpoints.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine.

### Installation
You can install the `async-websocket-pool` using pip:
```
pip install async-websocket-pool
```

Please note that this project requires Python 3.10 or later.

## Usage

```python
from async_websocket_pool import connect, run_pool

async def on_message(message):
    print(message)

tasks = [
  lambda: connect(
      'ws://example1.com',
      on_message=on_message,
      timeout=5,
      handler_drain_timeout=2.0,
      handler_cancel_grace=0.5,
  ),
  lambda: connect(
      'ws://example2.com',
      on_message=on_message,
      timeout=5,
      handler_drain_timeout=2.0,
      handler_cancel_grace=0.5,
  ),
]

await run_pool(tasks)

```

### Reconnect and handler shutdown

`connect()` processes messages concurrently up to `max_concurrent_tasks`. When a connection
times out or disconnects, the library waits for in-flight `on_message` handlers to finish for
up to `handler_drain_timeout` seconds. Any handlers still running after that are cancelled, and
the client waits up to `handler_cancel_grace` more seconds before reconnecting.

This keeps reconnect latency bounded while still giving well-behaved handlers time to finish.
Library users are expected to write cancellation-friendly handlers.

## Built With

* [Poetry](https://python-poetry.org/docs/) - Packaging and dependency management

## Documentation

For more information, please refer to the full documentation.

## Contribution

Contributions are always welcome! Please read our contributing guide to learn about our development process, how to propose bugfixes and improvements, and how to build and test your changes.

## Authors

**mpol1t**

## License

This project is licensed under the MIT License
