from webradio import player
from frontend.utils import basepath
from hardware import SyncAnalogDigitalConverter, Button, LED
from hardware import Mapper, reset_callbacks
from signal import pause


suffix = "webradio"
filepath = "french_urls"
drop_bits = 4
volume_steps = 24
with open(filepath) as filelike:
    urls = [line.strip() for line in filelike]


def truncate_bits(value, n_bits):
    return value >> n_bits


def change_station(client, station):
    client.station = station


def change_volume(client, volume):
    client.volume = volume


def toggle_mute(client, led):
    client.muted = not client.muted
    led.toggle()


def toggle_prebuffering(client, led):
    client.prebuffering = not client.prebuffering
    led.toggle()


station_mapper = Mapper(
    n_bits=10 - drop_bits,
    n_parts=len(urls),
    preprocess=lambda value: value >> drop_bits,
    )
volume_mapper = Mapper(
    n_bits=10 - drop_bits,
    n_parts=volume_steps,
    preprocess=lambda value: value >> drop_bits,
    )


with basepath(suffix) as path:
    with player.Player(basepath=path, urls=urls, prebuffering=False) as client:
        mute_button = Button(pin=17)
        prebuffering_button = Button(pin=18)

        muted_led = LED(pin=22)
        prebuffered_led = LED(pin=23)

        station_slider = SyncAnalogDigitalConverter(channel=0)
        volume_knob = SyncAnalogDigitalConverter(channel=1)

        with reset_callbacks(
                mute_button,
                prebuffering_button,
                station_slider,
                volume_knob,
                ):
            # connect leds to buttons and assign actions
            mute_button.when_pressed = lambda: toggle_mute(client, muted_led)
            prebuffering_button.when_pressed = lambda: toggle_prebuffering(
                client,
                prebuffered_led,
                )

            station_slider.on_change = lambda value: change_station(
                station_mapper(value),
                )
            volume_knob.on_change = lambda value: change_volume(
                volume_mapper(value),
                )

            # wait until we get a signal
            pause()
