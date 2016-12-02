from webradio import pool, url
from frontend.utils import format_urls

path = "server_pool"
filepath = "urls"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

with pool.map(path, urls) as client_pool:
    print(format_urls(urls))
    while True:
        try:
            index = input("entry? ")
            client_pool.play(int(index))
        except ValueError:
            continue
        except RuntimeError:
            print(format_urls(urls))
        except EOFError:
            print("")
            break
        except BrokenPipeError:
            for client in client_pool.clients:
                print(client._client.ping())
