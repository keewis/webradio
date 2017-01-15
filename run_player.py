from frontend.utils import basepath
from frontend import synchronous
from webradio import player, url


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

# patch for prebuffering
synchronous.actions['prebuffering'] = lambda *, client: setattr(
    client,
    "prebuffering",
    not client.prebuffering,
    )

with basepath(suffix) as path:
    with player.Player(basepath=path, urls=urls, prebuffering=False) as client:
        synchronous.print_choices(urls)
        synchronous.print_prompt()
        while True:
            try:
                synchronous.process_input(client)
            except StopIteration:
                break
