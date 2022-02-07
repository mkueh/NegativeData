import pandas as pd
import Data_Import_Cleaning.Utils.Type_Conversion as Types
import Data_Import_Cleaning.Utils.SMILES_Tools as Smiles
import numpy as np


def isempty(df_element):
    """Checks if a given entry from a Pandas Dataframe is empty, i.e.
        - np.nan
        - None
        - empty string, list or dict

    Parameters:
        df_element (any): element of a dataframe, accessed by pd.at[...]

    Returns:
        isempty (bool)
    """
    if Types.is_single(df_element):
        if pd.isnull(df_element):
            return True
        if df_element == "":
            return True
        else:
            return False
    elif isinstance(df_element, list):
        if len(df_element) == 0:
            return True
        elif (len(df_element) == 1) and df_element[0] == "":
            return True
        else:
            return False
    else:
        return False


def convert_to_bool(dataframe, column_name):
    """Converts entries in a column to the corresponding Boolean (i.e. "True" to True, "False" to False")

    Parameters:
        dataframe (pd.DataFrame):
        column_name (str):

    Returns:
        dataframe (pd.DataFrame): Modified dataframe

    """
    for i in dataframe.index.values:
        dataframe.at[i, column_name] = Types.getbool(dataframe.at[i, column_name])

    return dataframe


def merge_smiles_lists_in_df(dataframe_old):
    """Merges lists of SMILES strings within a Pandas Dataframe to a single concatenated SMILES string.
    Empty strings are represented as NaN.

    Parameters:
        dataframe_old (pd.DataFrame): Original dataframe

    Returns:
        dataframe_new (pd.DataFrame): Modified dataframe
    """
    dataframe_new = pd.DataFrame(index=range(dataframe_old.shape[0]), columns=dataframe_old.columns.values)

    for i in dataframe_old.index.values:
        for j in dataframe_old.columns.values:
            if isinstance(dataframe_old.at[i, j], list):
                dataframe_new.at[i, j] = Smiles.concat_smiles(dataframe_old.at[i, j])
            else:
                dataframe_new.at[i, j] = dataframe_old.at[i, j]
    dataframe_new.replace("", np.NaN, regex=True, inplace=True)

    return dataframe_new
