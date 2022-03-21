import Data_Import_Cleaning.Utils.SMILES_Tools as Smi

def is_single(data):
    """Checks if data type is str/float/int/bool.

    Parameters:
        data (any type)

    Returns:
        boolean
    """
    if isinstance(data, (str, float, int, bool)) or data is None:
        return True
    else:
        return False


def round_down(number, base, accuracy):
    """Rounds number down to multipliers of a given base

    Parameters:
        number (int or float): number to be rounded
        base (int or float): base to multipliers of which rounding should be performed
        accuracy (int): number of significant decimal places, as given in python's internal round function

    Returns:
        rounded number (float)
    """
    return round(base * int(float(number) / float(base)), accuracy)


def getbool(data):
    """Gets boolean variables from string data (e.g. imported csv files). Returns the unmodified data otherwise (i.e. if the string is not True or False).

    Parameters:
        data (str): raw data

    Returns:
        data (bool or other type)
    """
    data_str = str(data)

    if data_str == "True":
        return True
    elif data_str == "False":
        return False
    else:
        return data_str


def convert_to(data, targetformat):
    """General converter of data (str, int, float, bool) to target type or data format. Also operates on lists (and returns the modified list then).

    Currently available target format / type:
        - str
        - int
        - float
        - bool
        - smiles (canonicalized SMILES)
        - rxn_smiles_sm (only starting material from reaction SMILES)
        - rxn_smiles_prod (only product from reaction SMILES)
        - cmpd_name (compound name)

    Parameters:
        data (str, bool, int, float, list)
        targetformat (str):

    Returns:
        new_data (defined target type)
    """
    new_data = None

    if isinstance(data, list):
        return [convert_to(i, targetformat) for i in data]

    if targetformat == "int":
        try:
            new_data = int(data)
        except ValueError:
            new_data = None

    elif targetformat == "float":
        try:
            new_data = float(data)
        except ValueError:
            new_data = None

    elif targetformat == "str":
        try:
            new_data = str(data)
        except ValueError:
            new_data = None

    elif targetformat == "bool":
        try:
            new_data = getbool(data)
        except ValueError:
            new_data = None

    elif targetformat == "smiles":
        try:
            new_data = Smi.canonicalize(data)
        except ValueError:
            new_data = None

    elif targetformat == "rxn_smiles_sm":
        #try:
        new_data = Smi.split_rxn_smiles(data)[0]
        #except (ValueError, AttributeError):
        #    new_data = []

    elif targetformat == "rxn_smiles_prod":
        try:
            new_data = Smi.split_rxn_smiles(data)[2]
        except (ValueError, AttributeError):
            new_data = []

    elif targetformat == "cmpd_name":
        try:
            new_data = [x.strip() for x in data.split(";")]
        except AttributeError:
            new_data = []

    return new_data
