from gpiozero.threads import GPIOThread

from .mcp3002 import MCP3002


class PollThread(GPIOThread):
    def __init__(self, adc, func):
        super().__init__(target=self.continuously_call, args=(adc, func))

    def continuously_call(self, adc, func):
        while not self.stopping.is_set():
            value = adc.value
            func(value)


class PollingMixin(object):
    def __init__(self, connected_adc):
        self.adc = connected_adc

        self._on_change = None
        self._thread = None

    @property
    def on_change(self):
        return self._on_change

    @on_change.setter
    def on_change(self, func):
        if self._thread is not None:
            self._thread.stop()

        self._on_change = func
        self._thread = PollThread(self.adc, self._on_change)
        self._thread.start()


class SyncAnalogDigitalConverter(PollingMixin):
    def __init__(self, *args, **kwargs):
        self.adc = MCP3002(*args, **kwargs)

        super().__init__(self.adc)


if __name__ == "__main__":
    import time
    import sys

    if len(sys.argv[1:]) < 1:
        channel = 0
    else:
        channel = int(sys.argv[1])
    adc = SyncAnalogDigitalConverter(channel=channel, differential=False)

    def print_value(value):
        print(value)

    adc.on_change = print_value

    # wait five seconds for the values to print
    time.sleep(5)
