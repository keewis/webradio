from webradio import player, url
from frontend.utils import basepath
from frontend import asynchronous
import asyncio
import sys


def read_urls(filelike):
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]
    return urls


def reader(pool):
    task = asyncio.async(asynchronous.process_input(pool))
    asyncio.wait(task)


if __name__ == "__main__":
    suffix = "webradio_pool"
    filepath = "english_urls"
    with open(filepath) as filelike:
        urls = read_urls(filelike)

    asynchronous.actions['prebuffering'] = lambda *, client: setattr(
        client,
        "prebuffering",
        not client.prebuffering,
        )

    with basepath(suffix) as p:
        with player.map(basepath=p, urls=urls, prebuffering=False) as c, \
                asynchronous.run_loop_forever() as loop:
            asyncio.async(asynchronous.print_choices(c.urls))
            asyncio.async(asynchronous.print_prompt())
            loop.add_reader(sys.stdin, reader, c)
