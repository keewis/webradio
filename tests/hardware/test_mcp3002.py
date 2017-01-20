import pytest
from unittest import mock

import _gpiozero
import hardware.mcp3002 as mcp3002


@pytest.fixture(scope='function')
def mcp_spi():
    m = mock.patch(
        'hardware.mcp3002.MCP3002._spi',
        mock.create_autospec(_gpiozero.MCP3002._spi),
        )

    with m as _spi:
        yield _spi


def test_mcp3002_read(mcp_spi):
    channel = 0
    adc = mcp3002.MCP3002(channel=channel)

    expected_message = [192, 0]
    raw_result = [7, 250]
    mcp_spi.transfer.return_value = raw_result
    expected_result = sum(
        value * 2 ** (index * 8)
        for index, value in enumerate(reversed(raw_result))
        )

    result = adc._read()
    assert result == expected_result
    assert mcp_spi.transfer.call_args_list[0] == mock.call(expected_message)
