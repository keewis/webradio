from webradio import pool, url
import asyncio
import sys


def read_urls(filelike):
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]
    return urls


@asyncio.coroutine
def print_choices(urls):
    for index, _url in enumerate(urls):
        print("({}): {}".format(index, _url))
    print("> ", end='')
    sys.stdout.flush()


@asyncio.coroutine
def switch_channel(pool, index):
    pool.play(int(index))


def reader(pool):
    task = asyncio.async(process_input(pool))
    asyncio.wait(task)


@asyncio.coroutine
def process_input(pool):
    try:
        data = sys.stdin.readline()
        if len(data.strip()) == 0:
            raise EOFError("end of program")
        print("> ", end='')
        sys.stdout.flush()
        yield from switch_channel(pool, data)
    except (ValueError, RuntimeError):
        sys.stdout.write("\n")
        yield from print_choices(pool.urls)
    except (EOFError, KeyboardInterrupt):
        print("")
        loop = asyncio.get_event_loop()
        loop.stop()


if __name__ == "__main__":
    path = "server_pool"
    filepath = "urls"
    with open(filepath) as filelike:
        urls = read_urls(filelike)

    loop = asyncio.get_event_loop()

    with pool.map(basepath=path, urls=urls) as cp:
        asyncio.async(print_choices(cp.urls))
        loop.add_reader(sys.stdin, reader, cp)

        try:
            loop.run_forever()
        finally:
            loop.close()
