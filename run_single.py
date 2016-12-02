from frontend.utils import basepath, format_urls
from webradio import single, url


suffix = "webradio"
filepath = "urls2"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

with basepath(suffix) as path, single.map(path, urls) as client:
    client.volume = 50
    print(client.server.socket)
    print(format_urls(urls))

    while True:
        try:
            index = input("entry? ")
            client.play(int(index))
        except ValueError:
            continue
        except RuntimeError:
            print(format_urls(urls))
        except EOFError:
            print("")
            break
