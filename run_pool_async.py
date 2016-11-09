from frontend.utils import basepath
from frontend import asynchronous
from webradio import pool
import asyncio
import sys


def read_urls(filelike):
    urls = [line.strip() for line in filelike]
    return urls


def reader(pool):
    task = asyncio.async(asynchronous.process_input(pool))
    asyncio.wait(task)


if __name__ == "__main__":
    suffix = "webradio_pool"
    filepath = "urls"
    with open(filepath) as filelike:
        urls = read_urls(filelike)

    with basepath(suffix) as p:
        with pool.map(basepath=p, urls=urls) as cp, \
                asynchronous.run_loop_forever() as loop:
            asyncio.async(asynchronous.print_choices(cp.urls))
            asyncio.async(asynchronous.print_prompt())
            loop.add_reader(sys.stdin, reader, cp)
