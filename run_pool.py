from webradio import pool, url
import time

path = "server_pool"
filepath = "urls"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

index = 1

server_pool = pool.Server(basepath=path, num=len(urls))
client_pool = pool.Client(server=server_pool)
client_pool.set(urls)


def print_choices():
    for index, _url in enumerate(urls):
        print("({}): {}".format(index, _url))

print_choices()
while True:
    try:
        index = input("entry? ")
        client_pool.play(int(index))
    except ValueError:
        continue
    except RuntimeError:
        print_choices()
    except EOFError:
        print("")
        break
    except BrokenPipeError:
        for client in client_pool.players:
            print(client._client.ping())
        client_pool = pool.Client(server=server_pool)
        client_pool.set(urls)

time.sleep(10)
del client_pool
