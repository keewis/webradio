def split_into_equal_parts(input_list, number_of_parts):
    """ Splits a list into a list of sublists

    Arguments
    ----------
    a_list : list object
        List wich will be split into Sublists
    number_of_parts : int
        Number of sublists which should be created

    Returns
    -------
    seperated_lists : list of lists
        List of Sublists of the given list which are as equal sized as possible
    """
    start = 0
    separated_lists = []
    for i in range(number_of_parts):
        end = round((len(input_list) / number_of_parts) * (i + 1))
        separated_lists.append(input_list[start:end])
        start = end
    return separated_lists
