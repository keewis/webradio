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
    bits_per_word = 8

    def transfer(self, message):
        pass


class MCP3002(object):
    _spi = SPI()

    def __init__(self, channel=0, differential=False, bits=10, **spi_args):
        self._channel = channel
        self._differential = differential
        self._bits = bits

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

    @property
    def bits(self):
        return self._bits
