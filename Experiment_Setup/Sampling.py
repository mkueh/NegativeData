import Utils.Type_Conversion as Types
import random
import numpy.random as nprandom
import Utils.SMILES_Tools as Smi


class CategoricalDistribution:
    def __init__(self, data_dictionary, binsize, accuracy=3):
        """Creates the instance of a categorical distribution object.
        Sorts entries with categorical target variables into bins of given size.

        Parameters:
            data_dictionary (dict): Dictionary of experiment identifiers and target values (used for generation/assignment of bins).
            binsize (float): Size of the individual bins
            accuracy (int): Rounding accuracy for bin generation/assignment.

        Sets the following attributes:
            self.binsize (float): Size of the individual bins
            self.size (int): Number of data points
            self.rawdata (list): List of all experiment identifiers
            self.distribution (dict): Dictionary of all bin identifiers as keys and lists of all experiment identifiers as values.
            self.probabilities (dict): Dictionary of all bin identifiers as keys and bin probabilites as values.
            self.nobins (int): Number of bins
        """
        self.binsize = binsize
        self.size = len(data_dictionary)
        self.rawdata = list(data_dictionary.keys())
        self.distribution = dict()
        for entry in data_dictionary:
            rounded = Types.round_down(data_dictionary[entry], self.binsize, accuracy)
            try:
                self.distribution[rounded].append(entry)
            except KeyError:
                self.distribution[rounded] = [entry]

        self.probabilities = dict()
        for i in self.distribution:
            self.probabilities[i] = len(self.distribution[i]) / self.size

        self.nobins = len(self.distribution)
        self.bins = list(self.probabilities.keys())

    def sample_from(self, targetdistribution, final_length='max'):
        """Modifies the distribution by drawing a stratified sample.
        Probabilities for stratified sampling are taken from the target distribution.
            - determines the maximum possible length of a stratified distribution
            - iterates over bins and draws the appropriate number of random samples
            - re-sets self.distribution, self.rawdata, self.bins, self.probabilities, self.size

        Parameters:
            targetdistribution (CategoricalDistribution): Distribution to match after stratified sampling.
            final_length (float or "max"): Relative length of the stratified sample. Max draws a sample of the the maximum possible length.

        Returns:
            None
        """
        length = self.size
        for bin in targetdistribution.bins:
            length = min(length, len(self.distribution[bin]) / targetdistribution.probabilities[bin])
        if not final_length == 'max':
            length = int(final_length*length)

        length_new = 0
        distrib_new = dict()
        probabilities_new = dict()
        rawdata = []

        for bin in targetdistribution.bins:
            distrib_new[bin] = random.sample(self.distribution[bin], int(length*targetdistribution.probabilities[bin]))
            length_new = length_new + len(distrib_new[bin])
            rawdata = rawdata + distrib_new[bin]

        for bin in distrib_new:
            probabilities_new[bin] = len(distrib_new[bin]) / length_new

        self.rawdata = rawdata
        self.size = length_new
        self.bins = list(probabilities_new.keys())
        self.distribution = distrib_new
        self.probabilities = probabilities_new

    def oversample_from(self, targetdistribution, size="max"):
        """Modifies the distribution by oversampling
        Probabilities for oversampling are taken from the target distribution.
            - identifies the bin with the largest probability deviation from the target distribution
            - computes the number of oversamples to be drawn from each bin
            - performs the random oversampling and modifies self.distribution, self.rawdata, self.probabilities, self.size

        Parameters:
            targetdistribution (CategoricalDistribution): Distribution to match after oversampling.
            size (float or "max"): Relative size of the dataset after oversampling

        Returns:
            None
        """
        difference = dict()
        minimum = 0
        for bin in self.bins:
            difference[bin] = targetdistribution.probabilities[bin] - self.probabilities[bin]
            minimum = min(minimum, difference[bin])
        for bin in self.bins:
            difference[bin] = (difference[bin]-minimum)/(self.nobins*abs(minimum))

        if size == "max":
            n_tot = self.nobins*abs(minimum)*self.size
        else:
            n_tot = size*self.size

        for bin in self.bins:
            addition = random.choices(self.distribution[bin], k=int(n_tot*difference[bin]))
            self.distribution[bin] = self.distribution[bin] + addition
            self.rawdata = self.rawdata + addition
            self.size = self.size + len(addition)
        for bin in self.bins:
            self.probabilities[bin] = len(self.distribution[bin]) / self.size

    def oversample_from_single_bin(self, size, bin_identifier="min"):
        """Modifies the distribution by oversampling from a single bin.
        Probabilities for oversampling are taken from the target distribution.
            - identifies the bin with the largest probability deviation from the target distribution
            - computes the number of oversamples to be drawn from each bin
            - performs the random oversampling and modifies self.distribution, self.rawdata, self.probabilities, self.size

        Parameters:
            size (float or "max"): Relative amount of added datapoints.
            bin_identifier (float or "min"): Key of the bin to be sampled from.

        Returns:
            None
        """
        if bin_identifier == "min":
            bin_identifier = min(*self.bins)

        addition = random.choices(self.distribution[bin_identifier], k=int(self.size*size))
        self.distribution[bin_identifier] = self.distribution[bin_identifier] + addition
        self.rawdata = self.rawdata + addition
        self.size = self.size + len(addition)

        for bin in self.bins:
            self.probabilities[bin] = len(self.distribution[bin]) / self.size


def sample_distribution_from(data_dictionary_source, data_dictionary_target, binsize, size):
    """Function to perform stratified sampling on a given dataset.
    Returns a stratified sample from a source distribution which matches the probability distribution of a target distribution.

    Parameters:
        data_dictionary_source (dict): Dictionary of experiment identifiers and target values of the source distribution.
        data_dictionary_target (dict): Dictionary of experiment identifiers and target values of the target distribution.
        binsize (float): Size of the individual bins.
        size (float or "max"): Relative size (relativ to maximum) of the stratified sample.

    Returns:
        source_distribution.rawdata (list): List of sampled experiment identifiers from the source distribution.
    """
    source_distribution = CategoricalDistribution(data_dictionary_source, binsize)
    target_distribution = CategoricalDistribution(data_dictionary_target, binsize)

    source_distribution.sample_from(target_distribution, size)
    return source_distribution.rawdata


def oversample_from(data_dictionary_source, data_dictionary_target, binsize, size):
    """Function to perform oversampling on a given dataset.
    Returns a oversampled sample from a source distribution which matches the probability distribution of a target distribution.

    Parameters:
        data_dictionary_source (dict): Dictionary of experiment identifiers and target values of the source distribution.
        data_dictionary_target (dict): Dictionary of experiment identifiers and target values of the target distribution.
        binsize (float): Size of the individual bins.
        size (float or "max"): Relative size (relativ to maximum) of the added sample.

    Returns:
        source_distribution.rawdata (list): List of sampled experiment identifiers from the source distribution.
    """
    source_distribution = CategoricalDistribution(data_dictionary_source, binsize)
    target_distribution = CategoricalDistribution(data_dictionary_target, binsize)

    source_distribution.oversample_from(target_distribution, size)
    return source_distribution.rawdata


def oversample_from_single_bin(data_dictionary_source, binsize, size, bin_identifier):
    """Function to perform oversampling from a single bin in a given dataset.
    Returns an oversampled sample from a source distribution.

    Parameters:
        data_dictionary_source (dict): Dictionary of experiment identifiers and target values of the source distribution.
        binsize (float): Size of the individual bins.
        size (float or "max"): Relative size (relativ to maximum) of the added sample.
        bin_identifier (float or "min"): Identifier of the bin to sample from.

    Returns:
        source_distribution.rawdata (list): List of sampled experiment identifiers from the source distribution.
    """
    source_distribution = CategoricalDistribution(data_dictionary_source, binsize)
    source_distribution.oversample_from_single_bin(size, bin_identifier)

    return source_distribution.rawdata


def sample_random(index_list, number_entries):
    """Performs a random sampling from a given dataset.

    Parameters:
         index_list (list): List of experiment identifiers.
         number_entries (int): Number of samples to be drawn.

    Returns:
        sample (list): Sample of drawn experiment identifiers.
    """
    try:
        sample = random.sample(index_list, number_entries)
        return sample
    except ValueError:
        sample = index_list + random.choices(index_list, k=number_entries-len(index_list))
        return sample


def sample_from_gaussian(standard_deviation):
    """Draws a random sample from a Gaussian distribution centered at 0.0.

    Parameters:
        standard_deviation (float)

    Returns:
        value (float)
    """
    value = nprandom.normal(0.0, standard_deviation)
    return value


class DiscreteDistribution:
    def __init__(self, bin_list, raw_data_matrix):
        """Creates an instance of a distribution of discrete molecule names as bins.

        Parameters:
            bin_list (list): List of bin identifiers
            raw_data_matrix (list): List of lists of SMILES strings.

        Sets the following attributes:
            self.size (int): Number of bins
            self.distribution (dict): Dictionary of bin identifiers as keys and the number of occurences as values.

        """
        self.size = len(bin_list)
        self.distribution = dict()

        for bin_name in bin_list:
            counter = 0
            for entry in raw_data_matrix:
                if Smi.find_smiles_in_list(bin_name, entry):
                    counter = counter+1
            self.distribution[bin_name] = counter

    def write_to_csv(self, filename):
        """Writes the distribution (bin identifiers and occurences) to a csv file.

        Parameters:
            filename (str): Name of the csv file.

        Returns:
            None
        """
        with open(filename, 'w') as outfile:
            outfile.write("Compound,Occurences\n")
            for i in self.distribution.keys():
                outfile.write("{},{}\n".format(i, self.distribution[i]))
