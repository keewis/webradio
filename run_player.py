from webradio import player, url
from frontend.utils import basepath


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]


def print_choices(urls):
    for index, _url in enumerate(urls):
        print("({}): {}".format(index, _url))


def process_input(client, data):
    if data.startswith("vol"):
        volume = data.strip().split()[-1]
        client.volume = volume
    elif data.strip() == "mute":
        client.toggle_mute()
    elif data.startswith("prebuffering"):
        client.prebuffering = not client.prebuffering
    else:
        client.play(int(data.strip()))

with basepath(suffix) as path:
    with player.Player(basepath=path, urls=urls, prebuffering=False) as client:
        client.volume = 50
        print(client.server.socket)
        print_choices(urls)
        while True:
            try:
                data = input("> ")
                process_input(client, data)
            except ValueError:
                continue
            except RuntimeError:
                print_choices(urls)
            except EOFError:
                print("")
                break
