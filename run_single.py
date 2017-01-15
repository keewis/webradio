from frontend.utils import basepath, format_urls
from frontend import synchronous
from webradio import single, url


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

with basepath(suffix) as path, single.map(path, urls) as client:
    print(format_urls(urls))
    while True:
        try:
            synchronous.process_input(client)
        except StopIteration:
            break
