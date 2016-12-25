import frontend.asynchronous as asynchronous
import asyncio
import pytest


def test_run_loop_forever():
    @asyncio.coroutine
    def task(t):
        yield from asyncio.sleep(t)
        raise EOFError()

    # once we switch to python 3.5+, async is a keyword
    try:
        ensure_future = asyncio.ensure_future
    except AttributeError:
        ensure_future = asyncio.async

    with pytest.raises(EOFError):
        with asynchronous.run_loop_forever() as loop:
            long_running = task(10)
            ensure_future(long_running)
            loop.run_until_complete(task(0.01))
