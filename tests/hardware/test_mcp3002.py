import pytest
from unittest import mock

import _gpiozero
import hardware.mcp3002 as mcp3002


@pytest.fixture(scope='function')
def mcp():
    def patch_parent(class_):
        return type(class_.__name__, (mock.Mock,), dict(class_.__dict__))

    # no autospec to be able to run the test suite without
    # an installed gpiozero, and thus without being on the Raspberry Pi
    m = mock.patch(
        'hardware.mcp3002.MCP3002',
        type(
            mcp3002.MCP3002.__name__,
            (mock.Mock,),
            dict(mcp3002.MCP3002.__dict__),
            ),
        )

    with m as mcp:
        yield mcp


def test_mcp3002_read(mcp):
    adc = mcp3002.MCP3002(channel=0)

    expected_message = [192, 0]
    raw_result = [7, 250]
    adc._spi.transfer.return_value = raw_result
    expected_result = sum(
        value * 2 ** (index * 8)
        for index, value in enumerate(reversed(raw_result))
        )

    result = adc._read()
    assert result == expected_result
    assert adc._spi.transfer.call_args_list[0] == mock.call(expected_message)
