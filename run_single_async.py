from webradio import single, url
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
    path = "webradio_pool"
    filepath = "urls2"
    with open(filepath) as filelike:
        urls = read_urls(filelike)

    with basepath(path) as b:
        with single.map(basepath=b, urls=urls) as client, \
                asynchronous.run_loop_forever() as loop:
            asyncio.async(asynchronous.print_choices(client.urls))
            asyncio.async(asynchronous.print_prompt())
            loop.add_reader(sys.stdin, reader, client)
