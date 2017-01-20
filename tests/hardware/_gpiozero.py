""" fake gpiozero module

This module fakes the gpiozero interface to be able to test
gpiozero related functionality without actually having to have
the real one installed. Also, with the interface available,
tests can mock.autospec().
"""
import sys

try:
    import gpiozero
    del gpiozero
except ImportError:
    sys.modules['gpiozero'] = sys.modules[__name__]


class SPI(object):
    def transfer(self, message):
        pass


class MCP3002(object):
    _spi = SPI()

    def __init__(self, channel=0, differential=False, **spi_args):
        self._channel = channel
        self._differential = differential

    def _send(self):
        pass

    def _read(self):
        pass

    @property
    def differential(self):
        return self._differential

    @property
    def channel(self):
        return self._channel
