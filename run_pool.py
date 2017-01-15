from frontend.utils import basepath
from frontend import synchronous
from webradio import pool


suffix = "webradio_pool"
filepath = "english_urls"
with open(filepath) as filelike:
    urls = [line.strip() for line in filelike]

with basepath(suffix) as path:
    with pool.map(path, urls) as client:
        synchronous.print_choices(urls)
        synchronous.print_prompt()
        while True:
            try:
                synchronous.process_input(client)
            except StopIteration:
                break
