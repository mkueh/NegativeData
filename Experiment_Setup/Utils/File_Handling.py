import json


def write_to_file(object_to_write, filename, sepsign):
    """Writes an iterable (list, tuple, dictionary) into a csv-type file.

    Parameters:
          object_to_write (list or tuple or dict): Iterable object to be written.
          filename (str): Name of the target file.
          sepsign (str): csv separator to be used

    Returns:
          None
    """
    if isinstance(object_to_write, (list, tuple, dict)):
        with open("{}".format(filename), 'w') as outfile:
            for i in range(len(object_to_write)):
                if isinstance(object_to_write[i], (str, float, int)):
                    outfile.write("{}\n".format(object_to_write[i]))
                else:
                    for j in range(len(object_to_write[i]) - 1):
                        outfile.write("{}{}".format(object_to_write[i][j], sepsign))
                    outfile.write("{}\n".format(object_to_write[i][len(object_to_write[i]) - 1]))


def csv_to_dict(filename, sepsign=","):
    """Reads in a csv file as a dictionary (keys: first column, values: second column).

    Parameters:
        filename (str): Full path to the file.
        sepsign (str): csv-type separator

    Returns:
        result_dict (dict): Parsed dictionary
    """
    result_dict = dict()
    with open(filename, 'r') as csv_file:
        for row in csv_file:
            try:
                result_dict[row.split(sepsign)[0].strip()] = row.split(sepsign)[1].strip()
            except IndexError:
                result_dict[row.split(sepsign)[0].strip()] = ""
    return result_dict


def to_json(object_to_write, jsonfile):
    """Saves json-serializable object als .json file.

    Parameters:
        object_to_write (any json-serializable)
        jsonfile (str): Full path to the target file.

    Returns:
        None
    """
    with open(jsonfile, 'w') as outfile:
        json.dump(object_to_write, outfile)


def from_json(jsonfile):
    """Reads object from json file.

    Parameters:
        jsonfile (str): Full path to the json file.

    Returns:
        read_object
    """
    with open(jsonfile, 'r') as infile:
        read_object = json.load(infile)
    return read_object


def update_json_dict(jsonfile, dictionary):
    """Loads a dictionary from a json file, updates it by a given dictionary, and saves the json file.

    Parameters:
        jsonfile (str): Full path to the json file.
        dictionary (dict): Dictionary with updated/additional keys.

    Returns:
        None
    """
    dict_imported = from_json(jsonfile)
    dict_imported.update(dictionary)
    to_json(dict_imported, jsonfile)
