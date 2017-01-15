import asyncio
from contextlib import contextmanager
import sys

from . import utils


@contextmanager
def run_loop_forever():
    loop = asyncio.get_event_loop()

    try:
        yield loop
        loop.run_forever()
    finally:
        pending_tasks = (
            task
            for task in asyncio.Task.all_tasks(loop=loop)
            if not task.done()
            )

        for task in pending_tasks:
            task.cancel()
            task.set_result(None)

        loop.close()


@asyncio.coroutine
def print_prompt():
    print(utils.prompt, end='', flush=True)


@asyncio.coroutine
def print_choices(urls):
    print(utils.format_urls(urls))


@asyncio.coroutine
def switch_channel(client, index):
    client.play(index)


@asyncio.coroutine
def change_volume(client, new_volume):
    client.volume = new_volume


@asyncio.coroutine
def toggle_mute(client):
    client.toggle_mute()


actions = {
    'volume': lambda volume, *, client: change_volume(client, volume),
    'mute': lambda *, client: toggle_mute(client),
    'play': lambda index, *, client: switch_channel(client, index),
}


@asyncio.coroutine
def process_input(client):
    global actions
    try:
        data = sys.stdin.readline()
        if len(data.strip()) == 0:
            raise EOFError("end of program")

        action = utils.select_action(data, actions)
        yield from action(client=client)

        yield from print_prompt()
    except (ValueError, RuntimeError):
        yield from print_choices(client.urls)
        yield from print_prompt()
    except (EOFError, KeyboardInterrupt):
        print("")
        loop = asyncio.get_event_loop()
        loop.stop()
