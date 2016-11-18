import itertools


def split_into_equal_parts(input_sequence, number_of_parts):
    """ Splits a list into a list of sublists

    Arguments
    ----------
    input_sequence : sequence
        Sequence which will be split into approximately evenly sized iterables.
        In contrast to other approaches, this ensures that the median iterable
        is the largest (if necessary). The reason why this has to be a
        sequence is that for computing the number of elements per iterable
        we need to get the total number of elements via `len()` and to access
        individual elements via subscripting.
    number_of_parts : int
        Number of iterables which are to be created

    Yields
    ------
    seperated_iterable : iterable of iterables
        iterable of iterables which are as evenly sized as possible
    """
    total_length = len(input_sequence)
    ratio = total_length / number_of_parts
    indices = (
        (round(ratio * i), round(ratio * (i + 1)))
        for i in range(number_of_parts)
        )

    for start, end in indices:
        yield itertools.islice(input_sequence, start, end)
