from openbabel import openbabel
import pandas as pd
import progressbar as pb
import time
from sortedcontainers import SortedList

converter = openbabel.OBConversion()
converter.SetInAndOutFormats('smi', 'can')


def canonicalize(smiles):
    """Returns canonicalized SMILES string using openbabel.

    Parameters:
        smiles (str): raw SMILES

    Returns:
        smiles (str): canonicalized SMILES
    """
    if ((smiles.replace(" ", "")).replace("'", "")).strip() == "":
        return ""

    mol = openbabel.OBMol()
    converter.ReadString(mol, ((smiles.replace(" ", "")).replace("'", "")).strip())
    conversion = (converter.WriteString(mol)).strip()

    if conversion == "":
        raise ValueError("The string {} cannot be canonicalized.".format(smiles))
    else:
        return conversion


def canonicalize_list(smiles_list):
    """Canonicalizes a single SMILES string or a list of SMILES strings.

    Parameters:
        smiles_list (list or str)

    Returns:
        result_list (list) or newsmiles (str)
    """
    if isinstance(smiles_list, list):
        result_list = []
        for i in smiles_list:
            result_list.append(canonicalize_list(i))
        return result_list
    if isinstance(smiles_list, str):
        newsmiles = canonicalize(smiles_list)
        return newsmiles


def split_smiles_cmpd(concatsmiles):
    """Splits SMILES string of multiple compounds (separated by ".") into list of individual components.

    Parameters:
        concatsmiles (str)

    Returns:
        split (list): List of canonicalized individual SMILES
    """
    split = []
    for i in str(concatsmiles).split("."):
        split.append(canonicalize(i))
    split.sort()
    return split


def split_rxn_smiles(rxnsmiles):
    """Splits reaction SMILES into lists of individual reaction components

    Parameters:
        rxnsmiles (str):

    Returns:
        split (list): List consisting of three lists of SMILES strings [[reactants], [reagents], [products]]

    """
    if rxnsmiles.count(">") == 2:
        ed_prod = str(rxnsmiles).split(">")
        split = [[], [], []]
        for i in range(len(split)):
            split[i] = split_smiles_cmpd(ed_prod[i])
        return split
    else:
        raise ValueError("{} is not a valid reaction SMILES and cannot be split.".format(rxnsmiles))


def concat_smiles(compoundlist):
    """Merges list of compounds to one canonicalized SMILES (compounds separated by ".").

    Parameters:
        compoundlist (list): list of individual SMILES strings

    Returns:
        smiles (str)
    """
    if not compoundlist:
        return None
    else:
        try:
            compoundlist.sort()
        except:
            pass
        merger = ""
        for i in range(len(compoundlist)):
            if canonicalize(str(compoundlist[i]).strip("'")) != "":
                merger = merger + "." + str(compoundlist[i]).strip("'")
        return canonicalize(merger.strip("."))


def generate_rxn_smiles(starting_materials, products):
    """Generates reaction SMILES from starting materials and products.

    Parameters:
        starting_materials (list): list of SMILES strings of all starting materials
        products (str): smiles string of products

    Returns:
        rxn_smiles (str)
    """
    rxn_smiles = "{}>>{}".format(concat_smiles(starting_materials), products)
    return rxn_smiles


def find_smiles_in_list(smiles, list_of_smiles):
    """Checks for existance of all compounds within a SMILES string in a list of SMILES.

    Parameters:
        smiles (str): SMILES string to check (can consist of multiple molecules, separated by ".")
        list_of_smiles (list): list to search through

    Returns:
        present (bool): True if all compounds are present in list, False otherwise
    """
    smiles_split = split_smiles_cmpd(smiles)
    present = True
    for cmpd in smiles_split:
        if cmpd not in list_of_smiles:
            present = False
            break
    return present


def generate_onehot(dataframe_crd, target):
    """Generate a one-hot-encoded representation for each row of a given dataframe.

    Parameters:
        dataframe_crd (pd.DataFrame): Original dataframe to be encoded, format: n lines, m columns
        target (str): column name to be ignored for creating the one-hot encoding

    Returns:
        dataframe_new (pd.DataFrame): Dataframe as One-Hot encoding, format: n lines, 3 columns (OHE as string, Total Number of Compounds, Target)
    """
    cmpd_list = []
    columns_to_encode = dataframe_crd.columns.tolist()
    columns_to_encode.remove(target)

    print("Extracting the Compound List")
    for i in pb.progressbar(dataframe_crd.index.values, redirect_stdout=True):
        time.sleep(0.02)
        for column in columns_to_encode:
            cmpd_list = cmpd_list + split_smiles_cmpd(dataframe_crd.at[i, column])

    cmpd_list = SortedList(list(dict.fromkeys(cmpd_list)))
    dataframe_new = pd.DataFrame([], columns=["One Hot Encoding", "Number of Compounds", target])

    print("Generating the One-Hot Encoding")
    for i in pb.progressbar(dataframe_crd.index.values, redirect_stdout=True):
        time.sleep(0.02)

        onehot_list = []
        for column in columns_to_encode:
            for mol in split_smiles_cmpd(dataframe_crd.at[i, column]):
                if mol in cmpd_list:
                    onehot_list.append(cmpd_list.index(mol))
        onehot_list = list(dict.fromkeys(onehot_list))
        onehot_list.sort()

        onehot_str = ""
        for entry in onehot_list:
            onehot_str = onehot_str + " {}".format(entry)

        dataframe_new.at[i, "One Hot Encoding"] = onehot_str.strip()
        dataframe_new.at[i, "Number of Compounds"] = len(cmpd_list)
        dataframe_new.at[i, target] = dataframe_crd.at[i, target]

    return dataframe_new


def generate_rxnsmiles_dataset(dataframe_crd, dataset_settings):
    """Generate dataframe with reaction SMILES and target.

    Parameters:
        dataframe_crd (pd.DataFrame): Dataframe containing individual compound SMILES and targets, format n lines, m columns
        dataset_settings (dict): Dictionary with column information (data type for each column, role, ...)

    Returns:
        dataframe_new: Processed dataframe, format n rows, 2 columns (Reaction SMILES, Target)

    """
    print("Generating the Reaction SMILES Encoding.")
    dataframe_new = pd.DataFrame([], columns=["Reaction SMILES", dataset_settings["Target"]])
    for i in pb.progressbar(dataframe_crd.index.values, redirect_stdout=True):
        time.sleep(0.02)
        sm_list = []
        for j in dataframe_crd.columns.values:
            if (j != dataset_settings["Target"]) and (j != dataset_settings["Product"]):
                if ("smiles" in dataset_settings["Data Type"][j]) or ("cmpd" in dataset_settings["Data Type"][j]):
                    sm_list.append(dataframe_crd.at[i, j])
        dataframe_new.at[i, "Reaction SMILES"] = generate_rxn_smiles(sm_list, dataframe_crd.at[i, dataset_settings["Product"]])
        dataframe_new.at[i, dataset_settings["Target"]] = dataframe_crd.at[i, dataset_settings["Target"]]

    return dataframe_new
