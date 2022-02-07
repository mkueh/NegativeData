def apply_filters(input_value, filter_type):
    """Applies a given filter to the input variable

    Parameters:
        input_value
        filter_type (str): Name of the filter to be applied.

    """
    if filter_type == "contains_metal":
        return contains_metal(input_value)
    if filter_type == "no_metal":
        return no_metal(input_value)
    else:
        return None


def contains_metal(input_value):
    """Checks if an input (string or list of strings) contains a transition metal.

    Parameters:
        input_value (str or list[str])

    Returns:
        result (bool): True if input_value contains the metal, else False.
    """
    metals = ["Fe", "Ru", "Os", "Co", "Rh", "Ir", "Ni", "Pd", "Pt", "Cu", "Ag", "Au"]
    result = False

    if isinstance(input_value, list):
        for value in input_value:
            if contains_metal(value):
                result = True
                break

    if isinstance(input_value, str):
        for metal in metals:
            if metal in input_value:
                result = True

    return result


def no_metal(input_value):
    """Checks if an input (string or list of strings) does not contain any transition metal.

    Parameters:
        input_value (str or list[str])

    Returns:
        result (bool): True if input_value contains the metal, else False.
    """
    metals = ["Fe", "Ru", "Os", "Co", "Rh", "Ir", "Ni", "Pd", "Pt", "Cu", "Ag", "Au"]
    result = True

    if isinstance(input_value, list):
        for value in input_value:
            if not no_metal(value):
                result = False
                break

    if isinstance(input_value, str):
        for metal in metals:
            if metal in input_value:
                result = False

    return result
