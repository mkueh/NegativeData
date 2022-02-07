import Data_Import_Cleaning.Utils.SMILES_Tools as Smi
import Data_Import_Cleaning.Utils.File_Handling as Fh
import os
from urllib.request import urlopen


def convert_from_dictionary(mollist, jsonfile):
    """Generates conversion dictionary from a list of strings to the corresponding SMILES strings given a translation dictionary.

    Parameters:
        mollist (list): List of strings to translate
        jsonfile (str): json file containing the translation dictionary

    Returns:
        dictionary (dict): successfully translated strings (as keys) and the corresponding SMILES (as values)
        faillist (list): list of strings that were not contained in the translation dictionary.

    """
    dictionary = dict()
    faillist = []
    translation = Fh.from_json(jsonfile)

    for mol in mollist:
        if mol in translation.keys():
            dictionary[mol] = translation[mol]
        else:
            faillist.append(mol)

    return dictionary, faillist


def convert_with_opsin(mollist):
    """Generates conversion dictionary from a list of molecule names to the corresponding SMILES strings using the OPSIN tool as java application.
    (D.M. Lowe et al., J. Chem. Inf. Model. 2011, 51, 739)
    !!! IMPORTANT: REQUIRES THE PATH TO THE opsin.jar TO BE MODIFIED !!!

        - saves a list of molecules to a txt file
        - calls the OPSIN java application to perform the conversion (in Terminal)
        - reads in the output of the java application

    Parameters:
        mollist (list or str): Molecule name or list of molecule names.

    Returns:
        dictionary (dict): Dictionary of succcessfully translated molecule names (as keys) and SMILES strings (as values)
        faillist (list): List of non-translatable molecule names.
    """
    dictionary = dict()
    faillist = []
    if isinstance(mollist, str):
        mollist = [mollist]
    Fh.write_to_file(mollist, 'molfile.txt', ',')

    os.system('java -jar /Applications/opsin.jar molfile.txt smiles.txt >/dev/null')  # TO BE MODIFIED INDIVIDUALLY.

    with open("smiles.txt", 'r') as resultfile:
        linecounter = 0
        for line in resultfile:
            if line != "\n":
                dictionary[mollist[linecounter]] = Smi.canonicalize(line.strip())
            else:
                faillist.append(mollist[linecounter])
            linecounter = linecounter+1
    os.remove("molfile.txt")
    os.remove("smiles.txt")

    return dictionary, faillist


def convert_with_cactus(mollist):
    """Generates conversion dictionary from a list of molecules to the corresponding SMILES strings using the NIH CACTUS database.
    (http://cactus.nci.nih.gov/)

    Parameters:
        mollist (list or str): Molecule name or list of molecule names.

    Returns:
        dictionary (dict): Dictionary of succcessfully translated molecule names (as keys) and SMILES strings (as values)
        faillist (list): List of non-translatable molecule names.
    """
    dictionary = dict()
    faillist = []
    if isinstance(mollist, str):
        mollist = [mollist]
    for i in mollist:
        try:
            smiles = Smi.canonicalize(urlopen('http://cactus.nci.nih.gov/chemical/structure/{}/smiles'.format(i)).read().decode('utf8'))
            dictionary[i] = smiles
        except:
            faillist.append(i)
    return dictionary, faillist


def convert_string_to_smiles(mollist, jsonfile, failfile, update_jsonfile=True):
    """Generates conversion dictionary from a list of compound names to the corresponding SMILES strings by
        1. Lookup in a dictionary of known name–SMILES pairs (given as json file)
        2. Using the OPSIN converter.
        3. Querying the CACTUS database.

    Parameters:
        mollist (list or str): Molecule name or list of molecule names.
        jsonfile (str): Full path to json file containing the translation dictionary
        failfile (str): Full path to json file containing known molecules that failed to translate
        update_jsonfile (bool): Whether to update the translation dictionary with new successful translations.

    Returns:
        dictionary (dict): Dictionary of successfully translated molecule names(as keys) and their SMILES strings (as values).
    """
    if isinstance(mollist, str):
        mollist = [mollist]

    faillist = Fh.from_json(failfile)

    for mol in mollist:
        if mol in faillist:
            mollist.remove(mol)

    dictionary = dict()
    conversion, fails = convert_from_dictionary(mollist, jsonfile)
    dictionary.update(conversion)
    conversion, fails = convert_with_opsin(fails)
    dictionary.update(conversion)
    conversion, fails = convert_with_cactus(fails)
    dictionary.update(conversion)

    if update_jsonfile:
        Fh.update_json_dict(jsonfile, dictionary)
        faillist = faillist + fails
        Fh.to_json(faillist, failfile)

    return dictionary


def convert_list(mollist, dictionary):
    """Performs actual conversion of a list of names with a given conversion dictionary.

     Parameters:
         mollist (list): List of molecules to be translated
         dictionary (dict): Dictionary of names and SMILES strings.

    Returns:
        result_list (list): List of translations
     """
    result_list = []

    for i in mollist:
        try:
            result_list.append(dictionary[i])
        except KeyError:
            result_list.append("")

    return result_list
