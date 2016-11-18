import itertools
import pytest
from unittest import mock

from hardware import updates


@pytest.fixture(scope='function')
def player():
    m = mock.Mock()
    type(m).station = mock.PropertyMock()

    yield m


@pytest.fixture(scope='function')
def adc():
    m = mock.Mock()
    value = mock.PropertyMock()
    type(m).value = value

    yield m


def test_split_range():
    length = 11
    number = 3

    expected_result = [
        [0, 1, 2, 3],
        [4, 5, 6],
        [7, 8, 9, 10],
        ]
    result = list(map(
        list,
        updates.split_range(length, number),
        ))

    assert result == expected_result


def test_update_property(player, adc):
    property_name = "station"

    value_property = type(adc).__dict__['value']
    station_property = type(player).__dict__['station']

    # empty lookup table
    value = 0.1
    updater = updates.update_property(
        adc,
        player,
        property_name,
        lookup_table=None,
        )

    value_property.return_value = value
    updater()
    assert station_property.call_args_list[-1] == mock.call(10)

    # filled lookup table
    value = 0.02
    updater = updates.update_property(
        adc,
        player,
        property_name,
        lookup_table=updates.split_range(11, 4),
        )

    value_property.return_value = value
    updater()
    assert station_property.call_args_list[-1] == mock.call(0)
