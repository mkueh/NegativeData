import pandas as pd
import os


def readin_export(path_to_datafile, columns, column_names):
    """Read in Reaxys export (csv files).

    Parameters:
        path_to_datafile (str)
        columns (list): list of column names from Reaxys export to read
        column_names (list): list of column names to use for the final dataframe

    Returns:
        dataframe (pd.DataFrame)
    """
    dataframe = pd.read_csv(path_to_datafile, sep="\t", header=0, names=column_names, usecols=columns, encoding="latin1", on_bad_lines="skip")
    return dataframe


def merge_exports(directory, columns, column_names):
    """Merge different Reaxys exports (csv files) to one final dataframe.

    Parameters:
        directory (path): directory that contains all export files as csv files
        columns (list): columns to extract from Reaxys export
        column_names (list): names for the columns to use

    Returns:
        dataframe_extracted (pd.DataFrame)
    """
    filelist = os.listdir(directory)
    dataframe_extracted = None

    filecount = 0
    for file in filelist:
        if filecount == 0:
            dataframe_extracted = readin_export("{}/{}".format(directory, file), columns, column_names)
        else:
            print(file)
            dataframe_tmp = readin_export("{}/{}".format(directory, file), columns, column_names)
            dataframe_extracted = pd.concat([dataframe_extracted, dataframe_tmp], axis=0)
        filecount += 1

    indices_new = []
    for i in range(dataframe_extracted.shape[0]):
        indices_new.append(i)
    dataframe_extracted.index = indices_new

    return dataframe_extracted
