from webradio import single, url
from frontend.utils import basepath, format_urls
import asyncio
from contextlib import contextmanager
import sys


def read_urls(filelike):
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]
    return urls


@asyncio.coroutine
def print_choices(urls):
    print(format_urls(urls))
    print("> ", end='')
    sys.stdout.flush()


@asyncio.coroutine
def switch_channel(client, index):
    client.play(int(index))


@asyncio.coroutine
def change_volume(client, new_volume):
    client.volume = new_volume


@asyncio.coroutine
def toggle_mute(client):
    client.toggle_mute()


def reader(pool):
    task = asyncio.async(process_input(pool))
    asyncio.wait(task)


@asyncio.coroutine
def process_input(client):
    try:
        data = sys.stdin.readline()
        if len(data.strip()) == 0:
            raise EOFError("end of program")
        print("> ", end='')
        sys.stdout.flush()
        if data.strip() == "mute":
            yield from toggle_mute(client)
        elif "vol" in data:
            _, new_volume = data.strip().split()
            yield from change_volume(client, int(new_volume))
        else:
            yield from switch_channel(client, data)
    except (ValueError, RuntimeError):
        sys.stdout.write("\n")
        yield from print_choices(client.urls)
    except (EOFError, KeyboardInterrupt):
        print("")
        loop = asyncio.get_event_loop()
        loop.stop()


@contextmanager
def run_loop_forever():
    loop = asyncio.get_event_loop()

    try:
        yield loop
        loop.run_forever()
    finally:
        loop.close()


if __name__ == "__main__":
    path = "webradio_pool"
    filepath = "urls2"
    with open(filepath) as filelike:
        urls = read_urls(filelike)

    with basepath(path) as b:
        with single.map(basepath=b, urls=urls) as client, \
                run_loop_forever() as loop:
            asyncio.async(print_choices(client.urls))
            loop.add_reader(sys.stdin, reader, client)
