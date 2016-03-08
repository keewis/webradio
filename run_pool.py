from webradio import pool, url

path = "server_pool"
filepath = "urls"
with open(filepath) as filelike:
    raw_urls = [line.strip() for line in filelike]
    urls = [url.extract_playlist(_) for _ in raw_urls]

player_pool = pool.map(basepath=path, urls=urls)


def print_choices(urls):
    for index, _url in enumerate(urls):
        print("({}): {}".format(index, _url))

print_choices(urls)
while True:
    try:
        index = input("entry? ")
        player_pool.play(int(index))
    except ValueError:
        continue
    except RuntimeError:
        print_choices(urls)
    except EOFError:
        print("")
        break
    except BrokenPipeError:
        for client in player_pool.players:
            print(client._client.ping())
