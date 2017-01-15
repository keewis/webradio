from frontend.utils import basepath
from frontend import synchronous
from webradio import single, url


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

with basepath(suffix) as path, single.map(path, urls) as client:
    synchronous.print_choices(urls)
    synchronous.print_prompt()
    while True:
        try:
            synchronous.process_input(client)
        except StopIteration:
            break
