from frontend.utils import basepath
from frontend import synchronous
from webradio import single


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    urls = [line.strip() for line in filelike]

with basepath(suffix) as path:
    with single.map(path, urls) as client:
        synchronous.print_choices(urls)
        synchronous.print_prompt()
        while True:
            try:
                synchronous.process_input(client)
            except StopIteration:
                break
