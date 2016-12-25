import asyncio
from contextlib import contextmanager


@contextmanager
def run_loop_forever():
    loop = asyncio.get_event_loop()

    try:
        yield loop
        loop.run_forever()
    finally:
        loop.close()
