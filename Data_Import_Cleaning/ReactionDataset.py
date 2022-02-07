import pandas as pd
import Utils.Type_Conversion as Types
import Utils.SMILES_Tools as Smi
import Utils.Reaxys_Exports as Reaxys

from Utils.Logger import Logger
from DatasetSettings import DataframeSettings

import Utils.List_Handling as Lists
import String_to_SMILES.String_To_SMILES as Sts
import Utils.Dataframe_Tools as Dft
import Utils.File_Handling as Fh
import Filter
import os


class ReactionDataset:
    def __init__(self, basename, path, source):
        self.basename = basename
        self.settings = DataframeSettings(basename, path, source)
        self.log = Logger("{}Internal_Files/import.log".format(self.settings.path))
        self.dataset = None

    def import_data(self):
        """Imports a dataset according to the specified dataset/import settings.

        Parameters:

        Returns:
            None
        """
        self.log("Data Import Started.")
        dataframe_loaded = self.load_data()
        self.process_data(dataframe_loaded)


    def load_data(self):
        """Loads a dataset from the specified data source ("Reaxys" or "csv").

        Parameters:

        Returns:
            dataframe_exported (pd.DataFrame): Read dataframe
        """
        if self.settings.source == "Reaxys":
            dataframe_exported = Reaxys.merge_exports("{}Raw_Data".format(self.settings.path), self.settings.usecols, self.settings.usecols_str)

        if self.settings.source == "csv":
            dataframe_exported = pd.read_csv("{}Raw_Data/{}".format(self.settings.path, self.settings.filename), names=self.settings.usecols_str, usecols=self.settings.usecols)

        self.log("{} Data Points have been imported.".format(dataframe_exported.shape[0]))

        return dataframe_exported


    def process_data(self, dataframe_raw):
        """Processes the imported data according to the specifications in the import settings.
        Iterates twice over the full dataset.

        First Iteration:
            - modifies the data type of the respective columns / entries from the pd. readin standard to the target format
            - merges columns from the raw dataframe
            - collects all compound names to be translated to SMILES
            - scales numerical values

        Intermediate Processing:
            - drops columns that have become redundant after merging
            - generates translations of strings to SMILES

        Second Iteration:
            - translates strings in dataframe to SMILES
            - removes entries marked as "Delete if Column Empty"
            - removes entries by applying filters

        Parameters:

        Returns:
            None
        """
        self.log("Now adjusting the format of raw input data.")

        data_processed = pd.DataFrame([], columns=self.settings.settings_frame.index)

        ###################
        # FIRST ITERATION #
        ###################

        to_translate = Lists.SingleValueList([])

        for i in dataframe_raw.index.values:
            for column in self.settings.settings_frame.index:

                # Data Type Modification
                data_processed.at[i, column] = Types.convert_to(dataframe_raw.at[i, str(self.settings.settings_frame.at[column, "Column Number"])], self.settings.settings_frame.at[column, "Data Type"])

                # Merge Columns:
                if self.settings.settings_frame.at[column, "Merge"]:
                    data_processed.at[i, self.settings.settings_frame.at[column, "Merge"]] = data_processed.at[i, self.settings.settings_frame.at[column, "Merge"]] + data_processed.at[i, column]
                    data_processed.at[i, self.settings.settings_frame.at[column, "Merge"]].sort()

                # Collects Compound Names to be Translated to SMILES
                if self.settings.settings_frame.at[column, "Data Type"] == "cmpd_name":
                    to_translate.append(data_processed.at[i, column])

                # Scales Target Values
                if self.settings.settings_frame.at[column, "Data Type"] == "int" or self.settings.settings_frame.at[column, "Data Type"] == "float":
                    try:
                        data_processed.at[i, column] = data_processed.at[i, column] * self.settings.settings_frame.at[column, "Scale"]
                    except (KeyError, ValueError, TypeError):
                        pass

        self.log("The dataset now consists of {} entries".format(data_processed.shape[0]))

        ###########################
        # INTERMEDIATE PROCESSING #
        ###########################

        # Drop Columns after Merging
        for column in data_processed.columns.values:
            if self.settings.settings_frame.at[column, "Merge"]:
                data_processed.drop(columns=column, inplace=True)

        # Create String-to-SMILES Translation Dictionary
        self.log("Now converting compound names to SMILES.")
        to_translate.remove_duplicates()
        translated = Sts.convert_string_to_smiles(to_translate.list, "String_to_SMILES/string_to_smiles.json", "String_to_SMILES/non_convertible.json")

        ####################
        # SECOND ITERATION #
        ####################

        self.log("Now removing empty columns and applying filters.")
        emptycount = 0
        filtercount = 0

        for i in data_processed.index.values:
            for column in data_processed.columns.values:

                # Translate all Strings to SMILES
                if self.settings.settings_frame.at[column, "Data Type"] == "cmpd_name":
                    data_processed.at[i, column] = Sts.convert_list(data_processed.at[i, column], translated)

                # Delete Entries If Specific Columns are Empty
                if self.settings.settings_frame.at[column, "Delete_if_empty"]:
                    if Dft.isempty(data_processed.at[i, column]):
                        data_processed.drop(i, inplace=True)
                        emptycount = emptycount+1
                        break

                # Delete Entries by Applying Filters
                if self.settings.settings_frame.at[column, "Filter"] != "None":
                    if not Filter.apply_filters(data_processed.at[i, column], self.settings.settings_frame.at[column, "Filter"]):
                        data_processed.drop(i, inplace=True)
                        filtercount = filtercount+1
                        break

        data_processed.reset_index(drop=True, inplace=True)
        self.log("{} Data Points have been deleted as result of empty columns or failed translation.".format(emptycount))
        self.log("{} Data Points have been deleted as result of filter application.".format(filtercount))

        ###################
        # POST-PROCESSING #
        ###################

        self.log("Now removing duplicates.")
        self.dataset = Dft.merge_smiles_lists_in_df(data_processed)
        self.dataset.sort_values(self.settings.parameters["Target"], ascending=False, inplace=True)  # sorts by target so that upon duplicate removal, the entry with the highest target value is kept
        self.dataset.drop_duplicates(subset=[x for x in self.dataset.columns.values if x != self.settings.parameters["Target"]], inplace=True)
        self.dataset.sort_index(level=0, inplace=True)
        self.dataset.reset_index(drop=True, inplace=True)

        self.log("Import finished. {} Data Points remaining.".format(self.dataset.shape[0]))


    def save_state(self, path):
        """Saves the current state of data import (data + settings) as multiple .csv files:
            - SMILES representation
            - Reaction SMILES representation
            - One-Hot-Encoded representation
            - All representations
            - Dataset and Import Settings

        Parameters:
            path (str): Full path to the dataset-specific folder.

        Returns:
            None
        """

        self.save_as_csv(path)
        self.save_as_onehot(path)
        self.save_as_rxnsmiles(path)
        self.save_one_full_file(path)

        Fh.to_json(self.settings.parameters, "{}/Internal_Files/{}_Parameters.json".format(path, self.basename))


    def save_as_csv(self, path):
        """Save the loaded and processed dataset as a csv file.

        Parameters:
            path (str): Path to the folder where the csv file should be stored.

        Returns:
            None
        """
        if os.path.isfile("{}/Internal_Files/{}_INTERNAL.csv".format(path, self.basename)):
            pass
        else:
            self.dataset.to_csv("{}/Internal_Files/{}_INTERNAL.csv".format(path, self.basename), sep="\t", na_rep="NA")


    def save_as_onehot(self, path):
        """Converts compounds to a one-hot-encoded representation, saves that dataset as a csv file.

        Parameters:
            path (str): Path to the folder where the csv file should be stored.

        Returns:
            None
        """
        if os.path.isfile("{}/Internal_Files/{}_INTERNAL_Onehot.csv".format(path, self.basename)):
            pass
        else:
            onehot_results = Smi.generate_onehot(self.dataset, self.settings.parameters["Target"])
            onehot_results.to_csv("{}/Internal_Files/{}_INTERNAL_Onehot.csv".format(path, self.basename), sep="\t", na_rep="NA")


    def save_as_rxnsmiles(self, path):
        """Converts all compounds within the loaded and processed dataset to a reaction SMILES saves that dataset as a csv file.

        Parameters:
            path (str): Path to the folder where the csv file should be stored.

        Returns:
            None
        """
        if os.path.isfile("{}/Internal_Files/{}_INTERNAL_Rxnsmiles.csv".format(path, self.basename)):
            pass
        else:
            rxnsmiles_set = Smi.generate_rxnsmiles_dataset(self.dataset, self.settings.parameters)
            rxnsmiles_set.to_csv("{}/Internal_Files/{}_INTERNAL_Rxnsmiles.csv".format(path, self.basename), sep="\t", na_rep="NA")


    def save_one_full_file(self, path):
        """Generates one-hot-encoded representation and reaction SMILES representation from compounds within the current dataset.
        Saves all representations into a csv file.

        Parameters:
            path (str): Path to the folder where the csv file should be stored.

        Returns:
            None
        """
        dataset = pd.read_csv("{}/Internal_Files/{}_INTERNAL.csv".format(path, self.basename), sep="\t", header=0, index_col=0)
        onehot = pd.read_csv("{}/Internal_Files/{}_INTERNAL_Onehot.csv".format(path, self.basename), sep="\t", header=0, index_col=0)
        rxnsmiles = pd.read_csv("{}/Internal_Files/{}_INTERNAL_Rxnsmiles.csv".format(path, self.basename), sep="\t", header=0, index_col=0)

        dataset.insert(len(dataset.columns.values) - 1, "One Hot Encoding", onehot["One Hot Encoding"])
        dataset.insert(len(dataset.columns.values) - 1, "Number of Compounds", onehot["Number of Compounds"])
        dataset.insert(len(dataset.columns.values) - 1, "Reaction SMILES", rxnsmiles["Reaction SMILES"])

        dataset.to_csv("{}/Internal_Files/{}_all_representations.csv".format(path, self.basename), sep="\t", na_rep="NA")
