from . import utils


def split_range(length, number):
    return list(map(
        list,
        utils.split_into_equal_parts(range(length), number),
        ))


class update_property(object):
    def __init__(self, adc, player, property_name, lookup_table=None):
        self.property_name = property_name
        self.lookup_table = lookup_table
        self.adc = adc
        self.player = player

    def _get_index(self, adc_value):
        for index, sublist in enumerate(self.lookup_table):
            if adc_value not in sublist:
                continue

            return index

        raise RuntimeError("adc value {} not found".format(adc_value))

    def __call__(self):
        slider_value = int(self.adc.value * 100)

        if self.lookup_table is not None:
            index = self._get_index(slider_value)
        else:
            index = slider_value

        print("setting {} to {}".format(self.property_name, index))
        setattr(self.player, self.property_name, index)
