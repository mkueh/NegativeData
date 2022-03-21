import random


def k_random_splits(indices_all, n_splits, test_size):
    """Generates a defined number of random splits of a dataset.

    Parameters:
        indices_all (list): list of all experiment identifiers
        n_splits (int): number of splits to be generated
        test_size (float): relative size of the test set

    Returns:
        all_splits (list[tuple]): List of all train-test splits as tuples [([train], [test]), ([train], [test]), ...]
    """
    all_splits = []
    for i in range(n_splits):
        all_splits.append(random_split(indices_all, test_size))
    return all_splits


def random_split(indices_all, test_size):
    """Generates a random split of a dataset.

    Parameters:
        indices_all (list): list of all experiment identifiers
        test_size (float): relative size of the test dataset

    Returns:
        (trainsplit, testsplit) (tuple): Train and test dataset as lists of experiment identifiers

    """
    dataset_shuffled = random.sample(indices_all, len(indices_all))
    splitnumber = int((1 - test_size) * len(indices_all))
    trainsplit = dataset_shuffled[:splitnumber]
    testsplit = dataset_shuffled[splitnumber:]

    return trainsplit, testsplit


def k_fold_split(indices_all, n_splits):
    """Performs random k-fold splitting on a given dataset.

    Parameters:
        indices_all (list): list of all experiment identifiers
        n_splits (int): number of splits to generate

    Returns:
        all_splits (list[tuple]): List of all train-test splits as tuples [([train], [test]), ([train], [test]), ...]

    """
    dataset_shuffled = random.sample(indices_all, len(indices_all))
    bin_size = int(len(dataset_shuffled)/n_splits)
    all_splits = []
    dataset_split = []

    for i in range(n_splits):
        dataset_split.append(dataset_shuffled[(i*bin_size):((i+1)*bin_size)])
    for i in range(n_splits):
        training_data = []
        for j in range(n_splits):
            if j != i:
                training_data = training_data + dataset_split[j]
        all_splits.append([training_data, dataset_split[i]])

    return all_splits


def index_split(indices_all, splitindex):
    """Performs splitting of a dataset by index.

    Parameters:
        indices_all (list): list of all experiment identifiers
        splitindex (int): index to split the dataset

    Returns:
         alldata (list[tuple]): list of single split as a tuple [([train], [test])]
    """
    trainsplit = indices_all[:splitindex]
    testsplit = indices_all[splitindex:]
    return [(trainsplit, testsplit)]
