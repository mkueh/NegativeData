import os
import hjson
import pandas as pd


def generate_ml_output(raw_data, path, basename, jobname, models, train_index, test_index, target_column, type_dict, modify_targets=None, fixed_data=None):
    """Generates the input files and folders required for performing the individual ML computations using EasyChemML.
        1. Generates the output folder(s)
        2. Writes the train/test dataset and the settings.hjson files.

    Parameters:
        raw_data (str): Path to the folder where the "{basename}_INTERNAL.csv" / "{basename}_INTERNAL_Onehot.csv" / "{basename}_INTERNAL_Rxnsmiles.csv" are located.
        path (str): Path to the folder where the folders should be generated.
        basename (str): Base name of the data set / experiment
        jobname (str): Job name of the experiment to perform
        models (tuple): Tuple of ML models to generate the calculation folders for (currently: "MFF", "OHE", "BERT")
        train_index (list): indices of the training data points
        target_column (str): Name of the target column
        test_index (list): indices of the test data points
        type_dict (dict): Dictionary of column names in the original data set as keys, and data types as values
        modify_targets (function, optional): Function to apply to the target values of the training dataset.
        fixed_data (list, optional): indices of training data points where the target variable should not be modified

    Returns:
        None
    """
    create_folders(path, jobname, models)

    if "MFF" in models:
        trainset, testset = get_train_test_data("{}/{}_INTERNAL.csv".format(raw_data, basename), train_index, test_index)
        if modify_targets:
            trainset = modify_dataset_targets(trainset, list(set(train_index)-set(fixed_data)), target_column, modify_targets)
        write_dataset(trainset, testset, path, jobname, "MFF")
        generate_settings_mff(path, jobname, list(trainset.columns), target_column, type_dict, trainset.shape[0], trainset.shape[0] + testset.shape[0])

    if "OHE" in models:
        trainset, testset = get_train_test_data("{}/{}_INTERNAL_Onehot.csv".format(raw_data, basename), train_index, test_index)
        if modify_targets:
            trainset = modify_dataset_targets(trainset, list(set(train_index)-set(fixed_data)), target_column, modify_targets)
        write_dataset(trainset, testset, path, jobname, "OHE")
        generate_settings_ohe(path, jobname, target_column, trainset.shape[0], trainset.shape[0] + testset.shape[0])

    if "BERT" in models:
        trainset, testset = get_train_test_data("{}/{}_INTERNAL_Rxnsmiles.csv".format(raw_data, basename), train_index, test_index)
        if modify_targets:
            trainset = modify_dataset_targets(trainset, list(set(train_index)-set(fixed_data)), target_column, modify_targets)
        write_dataset(trainset, testset, path, jobname, "BERT")
        generate_settings_bert(path, jobname, target_column, trainset.shape[0], trainset.shape[0] + testset.shape[0])


def create_folders(path, jobname, models):
    """Creates the folders for performing calculations.

    Parameters:
        path (str): Path where folders should be created
        jobname (str): Job name of the experiment to perform
        models (tuple): Tuple of ML models to generate the calculation folders for (currently: "MFF", "OHE", "BERT")

    Returns:
        None
    """
    for model in models:
        foldername = "{}/{}_{}".format(path, jobname, model)
        if not os.path.exists(foldername):
            os.mkdir(foldername)


def get_train_test_data(filename, train_index, test_index):
    """Loads an existing dataset and returns train and test data as individual pandas dataframes.

    Parameters:
        filename (str): Path to the file that contains the raw data (including the correct representation).
        train_index (list): indices of the training data points
        test_index (list): indices of the test data points

    Returns:
        trainset (pd.DataFrame): Dataframe of training data points
        testset (pd.DataFrame): Dataframe of test data points
    """
    dataset = pd.read_csv(filename, sep="\t", header=0, index_col=0)
    trainset = dataset.loc[train_index]
    testset = dataset.loc[test_index]
    trainset.reset_index(drop=True, inplace=True)
    testset.reset_index(drop=True, inplace=True)
    return trainset, testset


def write_dataset(train_data, test_data, path, jobname, model):
    """Writes the dataset as a csv file, which can be read in by EasyChemML.

    Parameters:
        train_data (pd.DataFrame): Dataframe of the training data.
        test_data (pd.DataFrame): Dataframe of the test data
        path (str): Path where folders should be created
        jobname (str): Job name of the experiment to perform
        model (str): ML model to generate the data file for (currently: "MFF", "OHE", "BERT")

    Returns:
        None
    """
    dataset_towrite = train_data
    dataset_towrite = pd.concat([dataset_towrite, test_data], axis=0)
    dataset_towrite.to_csv("{}/{}_{}/input.csv".format(path, jobname, model), index=False, na_rep="NA")


def modify_dataset_targets(dataset, indices, target_column, function):
    """Modifies the target values for all indices in a given dataframe, returns the modified dataframe.

    Parameters:
        dataset (pd.DataFrame): Dataframe to be modified
        indices (list): Row indices for which the modification should be performed.
        target_column (str): Name of the target column
        function (function): Function (one float input variable) that modifies the target value.

    Returns:
        dataset (pd.DataFrame): Modified dataframe
    """
    for index in indices:
        dataset.at[index, target_column] = function(dataset.at[index, target_column])

    return dataset


def generate_settings_mff(path, jobname, all_columns, target_column, type_dict, train_size, dataset_size):
    """Generates the settings.hjson file for a MFF calculation using the EasyChemML program.

    Parameters:
        path (str): Path where ML folders should be created
        jobname (str): Job name of the experiment to perform
        all_columns (list): List of all column names in the dataset
        target_column (str): Name of the target column
        type_dict (dict): Dictionary of column names in the original data set as keys, and data types as values
        train_size (int): Size of the training dataset
        dataset_size (int): Size of the full dataset

    Returns:
          None
    """
    settings = load_hjson("Defaults/default_settings_MFF.hjson")

    columns = all_columns
    columns.remove(target_column)

    columns_to_encode = [column for column in all_columns if "smiles" not in type_dict[column] or "cmpd" not in type_dict[column]]

    settings['input_settings']['feature_colume'] = columns
    settings['input_settings']['feature_encoded'] = columns_to_encode
    settings['input_settings']['target_colume'] = [target_column]
    settings['splitter_settings']['outer_splittersettings']['testset_start'] = train_size
    settings['splitter_settings']['outer_splittersettings']['testset_end'] = dataset_size
    settings['output_settings']['nameforoutput'] = jobname

    save_hjson(settings, "{}/{}_MFF/settings.hjson".format(path, jobname))


def generate_settings_ohe(path, jobname, target_column, train_size, dataset_size):
    """Generates the settings.hjson file for an OHE calculation using the EasyChemML program.

    Parameters:
        path (str): Path where ML folders should be created
        jobname (str): Job name of the experiment to perform
        target_column (str): Name of the target column
        train_size (int): Size of the training dataset
        dataset_size (int): Size of the full dataset

    Returns:
          None
    """
    settings = load_hjson("Defaults/default_settings_OHE.hjson")

    settings['input_settings']['feature_colume'] = ["One Hot Encoding", "Number of Compounds"]
    settings['input_settings']['feature_encoded'] = ["One Hot Encoding", "Number of Compounds"]
    settings['input_settings']['target_colume'] = [target_column]
    settings['splitter_settings']['outer_splittersettings']['testset_start'] = train_size
    settings['splitter_settings']['outer_splittersettings']['testset_end'] = dataset_size
    settings['output_settings']['nameforoutput'] = jobname

    save_hjson(settings, "{}/{}_OHE/settings.hjson".format(path, jobname))


def generate_settings_bert(path, jobname, target_column, train_size, dataset_size):
    """Generates the settings.hjson file for a BERT calculation using the EasyChemML program.

    Parameters:
        path (str): Path where ML folders should be created
        jobname (str): Job name of the experiment to perform
        target_column (str): Name of the target column
        train_size (int): Size of the training dataset
        dataset_size (int): Size of the full dataset

    Returns:
          None
    """
    settings = load_hjson("Defaults/default_settings_BERT.hjson")

    settings['input_settings']['feature_colume'] = ["Reaction SMILES"]
    settings['input_settings']['feature_encoded'] = ["Reaction SMILES"]
    settings['input_settings']['target_colume'] = [target_column]
    settings['splitter_settings']['outer_splittersettings']['testset_start'] = train_size
    settings['splitter_settings']['outer_splittersettings']['testset_end'] = dataset_size
    settings['output_settings']['nameforoutput'] = jobname

    save_hjson(settings, "{}/{}_BERT/settings.hjson".format(path, jobname))


def load_hjson(hjsonfile):
    """Loads a hjson file and returns it as a dictionary.

    Parameters:
        hjsonfile (str): Path to the hjson file

    Returns:
        parameters (dict): Dictionary from the hjson file
    """
    with open(hjsonfile, 'r') as infile:
        parameters = hjson.load(infile)
    return parameters


def save_hjson(parameter_dict, filename):
    """Saves a dictionary as a hjson file.

    Parameters:
        parameter_dict (dict): Dictionary to save
        filename (str): Path to the target hjson file.

    Returns:
        None
    """
    with open(filename, 'w') as outfile:
        hjson.dump(parameter_dict, outfile)
