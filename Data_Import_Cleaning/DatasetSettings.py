import pandas as pd
import os
import Utils.Type_Conversion as Types
import Utils.Dataframe_Tools as Dft


class DataframeSettings:
    def __init__(self, basename, path, source):

        self.source = source
        self.path = "{}/".format(path, basename)
        print(self.path)

        if self.source == "csv":
            self.filename = [file for file in os.listdir("{}Raw_Data/".format(self.path)) if ".csv" in file][0]
        else:
            self.filename = None

        self.parameters = dict()
        self.parameters["Data Type"] = dict()

        self.settings_frame = None
        self.usecols = []
        self.usecols_str = []

        self.load_settings_file()


    def load_settings_file(self):
        """Loads and parses the .csv file of data import settings.

        Parameters:

        Returns:
            None
        """
        self.settings_frame = pd.read_csv("{}Import_Settings.csv".format(self.path), index_col=0)

        self.settings_frame = Dft.convert_to_bool(self.settings_frame, "Delete_if_empty")
        self.settings_frame = self.settings_frame.astype({"Column Number": int})
        self.settings_frame["Scale"] = pd.to_numeric(self.settings_frame["Scale"], errors="coerce")
        self.settings_frame = self.settings_frame.astype({"Scale": float})

        for i in self.settings_frame.index:
            self.settings_frame.at[i, "Merge"] = Types.getbool(self.settings_frame.at[i, "Merge"])
            if self.settings_frame.at[i, "Role"] == "Target":
                self.parameters["Target"] = i
            if self.settings_frame.at[i, "Role"] == "Product":
                self.parameters["Product"] = i
            self.parameters["Data Type"][i] = self.settings_frame.at[i, "Data Type"]

        self.usecols = [int(self.settings_frame.at[index, "Column Number"]) for index in self.settings_frame.index]
        self.usecols = list(dict.fromkeys(self.usecols))
        self.usecols.sort()

        self.usecols_str = [str(colname) for colname in self.usecols]
