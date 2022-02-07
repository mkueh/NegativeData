import Data_Import_Cleaning.Utils.Type_Conversion as Types


class SingleValueList:
    def __init__(self, value):
        """Creates the instance of a list which can only contain "single" data types (i.e. int, float, str, bool).

        Parameters:
            value (str, int, float, bool, list): First entry to the SingleValueList
        """
        self.list = []
        self.append(value)

    def append(self, appendix):
        """Appends "single" data types to the list. If a list is passed, each element is separately appended (works recursively).

        Parameters:
            appendix (str, int, float, bool, list): Entry to be appended

        Returns:
            None
        """
        if Types.is_single(appendix):
            self.list.append(appendix)

        elif isinstance(appendix, list):
            for item in appendix:
                self.append(item)


    def convert_to(self, targetformat):
        """Convert all elements within the list to a given data type.

        Parameters:
            targetformat (str): Name of the target format

        Returns:
            None
        """
        for i in range(len(self.list)):
            self.list[i] = Types.convert_to(self.list[i], targetformat)


    def remove_duplicates(self):
        """Removes duplicates from the list (via dict.fromkeys()).

        Parameters:

        Returns:
            None
        """
        self.list = list(dict.fromkeys(self.list))


    def sort(self):
        """Sorts elements within the list.

        Parameters:

        Returns:
            None
        """
        self.list = self.list.sort()
