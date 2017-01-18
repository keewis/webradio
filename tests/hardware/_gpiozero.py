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
    def transfer(message):
        pass


class MCP3002(object):
    def __init__(self, channel=0, differential=False, **spi_args):
        pass

    _spi = SPI()

    def _send(self):
        pass

    def _read(self):
        pass

    @property
    def differential(self):
        pass

    @property
    def channel(self):
        pass
