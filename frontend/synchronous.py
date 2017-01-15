import sys

from . import utils


actions = {
    'volume': lambda volume, *, client: setattr(client, "volume", volume),
    'mute': lambda *, client: client.toggle_mute(),
    'play': lambda index, *, client: client.play(index),
    }


def print_choices(urls):
    print(utils.format_urls(urls))


def print_prompt():
    print(utils.prompt, end='', flush=True)


def process_input(client):
    global actions

    try:
        data = sys.stdin.readline()
        if len(data.strip()) == 0:
            raise EOFError("end of program")

        action = utils.select_action(data, actions)
        action(client=client)

        print_prompt()
    except (ValueError, RuntimeError):
        print_choices(client.urls)
        print_prompt()
    except (EOFError, KeyboardInterrupt):
        print("")
        raise StopIteration()
