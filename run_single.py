from frontend.utils import basepath
from webradio import single, url


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]


def print_choices(urls):
    for index, _url in enumerate(urls):
        print("({}): {}".format(index, _url))

with basepath(suffix) as path, single.map(path, urls) as client:
    client.volume = 50
    print(client.server.socket)
    print_choices(urls)
    while True:
        try:
            index = input("entry? ")
            client.play(int(index))
        except ValueError:
            continue
        except RuntimeError:
            print_choices(urls)
        except EOFError:
            print("")
            break
