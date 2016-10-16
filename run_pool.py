from webradio import pool, url

path = "server_pool"
filepath = "urls"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]


def print_choices(urls):
    for index, _url in enumerate(urls):
        print("({}): {}".format(index, _url))

with pool.map(path, urls) as client_pool:
    print_choices(urls)
    while True:
        try:
            index = input("entry? ")
            client_pool.play(int(index))
        except ValueError:
            continue
        except RuntimeError:
            print_choices(urls)
        except EOFError:
            print("")
            break
        except BrokenPipeError:
            for client in client_pool.clients:
                print(client._client.ping())
