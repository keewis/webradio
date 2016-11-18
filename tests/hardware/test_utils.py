from hardware import utils


def test_split_into_equal_parts():
    initial_list = list(map(lambda _: "x{}".format(_), range(11)))

    # into 2 sublists
    expected_result = [
        ["x0", "x1", "x2", "x3", "x4", "x5"],
        ["x6", "x7", "x8", "x9", "x10"],
        ]
    result = list(map(list, utils.split_into_equal_parts(initial_list, 2)))

    assert result == expected_result

    # into 3 sublists
    expected_result = [
        ["x0", "x1", "x2", "x3"],
        ["x4", "x5", "x6"],
        ["x7", "x8", "x9", "x10"],
        ]
    result = list(map(list, utils.split_into_equal_parts(initial_list, 3)))

    assert result == expected_result

    # into 4 sublists
    expected_result = [
        ["x0", "x1", "x2"],
        ["x3", "x4", "x5"],
        ["x6", "x7"],
        ["x8", "x9", "x10"],
        ]
    result = list(map(list, utils.split_into_equal_parts(initial_list, 4)))

    assert result == expected_result

    # into 5 sublists
    expected_result = [
        ["x0", "x1"],
        ["x2", "x3"],
        ["x4", "x5", "x6"],
        ["x7", "x8"],
        ["x9", "x10"],
        ]
    result = list(map(list, utils.split_into_equal_parts(initial_list, 5)))

    assert result == expected_result

    # into 10 sublists
    expected_result = [
        ["x0"],
        ["x1"],
        ["x2"],
        ["x3"],
        ["x4", "x5"],
        ["x6"],
        ["x7"],
        ["x8"],
        ["x9"],
        ["x10"],
        ]
    result = list(map(list, utils.split_into_equal_parts(initial_list, 10)))

    assert result == expected_result
