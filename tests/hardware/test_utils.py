from hardware import utils


def test_split_into_equal_parts():
    initial_list = list(map(lambda _: "x{}".format(_), range(11)))
    expected_result = [
        ["x0", "x1"],
        ["x2", "x3"],
        ["x4", "x5", "x6"],
        ["x7", "x8"],
        ["x9", "x10"],
        ]

    assert utils.split_into_equal_parts(initial_list, 5) == expected_result
