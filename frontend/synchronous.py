import sys

from . import utils


def print_choices(urls):
    print(utils.format_urls(urls))


def print_prompt():
    print(utils.prompt, end='', flush=True)


def process_input(client):
    try:
        data = sys.stdin.readline()
        if len(data.strip()) == 0:
            raise EOFError("end of program")

        if data.strip() == "mute":
            client.toggle_mute()
        elif "vol" in data:
            _, new_volume = data.strip().split()
            client.volume = int(new_volume)
        elif "help" in data:
            raise ValueError()
        else:
            client.play(int(data))

        print_prompt()
    except (ValueError, RuntimeError):
        print_choices(client.urls)
        print_prompt()
    except (EOFError, KeyboardInterrupt):
        print("")
        raise StopIteration()
