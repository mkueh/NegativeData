import pandas as pd
from Splitter import k_random_splits
from generate_easychemml_output import generate_ml_output
from Sampling import sample_distribution_from, sample_random, oversample_from, oversample_from_single_bin, sample_from_gaussian


class SamplingExperiments:
    def __init__(self, raw_data, basename, data_types, target_column, destination_folder):
        """Instantiates a generator for sampling experiments.

        Parameters:
            raw_data (str): Path to the folder where the raw data ("{basename}_INTERNAL.csv" / "{basename}_INTERNAL_Onehot.csv" / "{basename}_INTERNAL_Rxnsmiles.csv") is located.
            basename (str): Base name of the data set / experiment
            data_types (dict): Dictionary of data types for all columns in the dataframe.
            target_column (str): Name of the target column in the dataset.
            destination_folder (str): Path to the folder where the folders should be generated.
        """
        self.basename = basename
        self.raw_data = raw_data
        self.dataset = pd.read_csv(f"{raw_data}/{basename}_INTERNAL.csv", sep="\t", header=0, index_col=0)
        self.all_indices = list(self.dataset.index.values)
        self.data_types = data_types
        self.target_column = target_column
        self.destination_folder = destination_folder

    def save_splits_for_ml(self, splits, name, **kwargs):
        """Saves generated train-test splits (given by indices) as EasychemML-processable files / folders.

        Parameters:
            splits (list[tuple]): List of train-test splits, each split as a (train_indices, test_indices) tuple.
            name (str): Name of the experiment.
            kwargs: Information on whether to post-modify target values ("modify_targets" and "fixed_data" kws)

        Returns:
            None
        """
        for i, split in enumerate(splits):
            experiment_name = f"{self.basename}_{name}_{i}"
            if "fixed_data" in kwargs:
                generate_ml_output(self.raw_data, self.destination_folder, self.basename, experiment_name, ("MFF", "OHE", "BERT"), split[0], split[1], self.target_column, self.data_types, kwargs["modify_targets"], kwargs["fixed_data"][i])
            else:
                generate_ml_output(self.raw_data, self.destination_folder, self.basename, experiment_name, ("MFF", "OHE", "BERT"), split[0], split[1], self.target_column, self.data_types)

    def index_target_dict(self, indices):
        """Get a dictionary of indices and corresponding target values from the dataset dictionary.

        Parameters:
            indices (list): List of indices

        Returns:
            index_target (dict)
        """
        index_target = {index: self.dataset.at[index, self.target_column] for index in indices}
        return index_target

    def random_splits(self, n_splits, split_ratio):
        """Creates n random splits and saves the corresponding EasychemML input folders.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set

        Returns:
            None
        """
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)
        self.save_splits_for_ml(splits, "random")

    def random_splits_abs_noise(self, n_splits, split_ratio, noise_levels):
        """Simulates absolute noise of varying degrees on the training data set.
            1. Generates k random splits of the data set.
            2. Simulates Gaussian noise on the training data.
            3. Operation 2 can be performed for varying standard deviations.
            4. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            noise_levels (list): List of standard deviations of noise applied
        """
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)

        for noise in noise_levels:
            def target_modifier(target):
                modified_value = target + sample_from_gaussian(noise)
                final_value = max(0.0, min(1.0, modified_value))
                return final_value

            self.save_splits_for_ml(splits, f"random_abs_noise_{noise}", modify_targets=target_modifier, fixed_samples=[])

    def random_splits_rel_noise(self, n_splits, split_ratio, noise_levels):
        """Simulates relative noise of varying degrees on the training data set.
            1. Generates k random splits of the data set.
            2. Simulates Gaussian noise on the training data.
            3. Operation 2 can be performed for varying standard deviations.
            4. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            noise_levels (list): List of standard deviations of noise applied
        """
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)

        for noise in noise_levels:
            def target_modifier(target):
                modified_value = target * (1 + sample_from_gaussian(noise))
                final_value = max(0.0, min(1.0, modified_value))
                return final_value

            self.save_splits_for_ml(splits, f"random_rel_noise_{noise}", modify_targets=target_modifier, fixed_samples=[])

    def split_sample(self, n_splits, split_ratio, target_dataset, target_column, subset, sizes):
        """Performs stratified sampling on random splits of the data set. Generates the output files for EasyChemML.
            1. Generates k random splits of the data set.
            2. Performs stratified sampling from distribution in given target dataset.
            3. Generates a randomly drawn control split of identical dimensionality.
            4. Can perform operations 2 and 3 for different relative sizes of the drawn sample (0 to "max" as max. size)
            5. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            target_dataset (pd.DataFrame): Dataset with the desired distribution of target values.
            target_column (str): Name of the target column in target_dataset
            subset (list): Sampling from "train", "test" or both
            sizes (list): List of relative sizes of the drawn sample (e.g. [0.2, 0.4, 0.6, 0.8, 1] or [0.5, "max"])

        Returns:
            None
        """
        # STEP 1: GENERATION OF RANDOM SPLITS
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)
        target_data = {index: target_dataset.at[index, target_column] for index in target_dataset.index.values}

        for size in sizes:
            splits_final = {"experiment": [], "control": []}
            for split in splits:
                train, train_control = split[0], split[0]
                test, test_control = split[1], split[1]

                # STEP 2+3: STRATIFIED SAMPLING + GENERATION OF RANDOMLY SAMPLED CONTROL
                if "train" in subset:
                    train = sample_distribution_from(self.index_target_dict(split[0]), target_data, 0.1, size)
                    train_control = sample_random(split[0], len(train))
                if "test" in subset:
                    test = sample_distribution_from(self.index_target_dict(split[1]), target_data, 0.1, size)
                    test_control = sample_random(test, len(test))

                # STEP 5: SAVE SPLITS FOR ML COMPUTATIONS
                splits_final["experiment"].append((train, test))
                splits_final["control"].append((train_control, test_control))

            self.save_splits_for_ml(splits_final["experiment"], f"stratified_sampling_{size}")
            self.save_splits_for_ml(splits_final["control"], f"stratified_sampling_{size}_control")

    def split_sample_add_random(self, n_splits, split_ratio, target_dataset, target_column, subset, sizes, add_amounts):
        """Performs stratified sampling on random splits of the data set.
        Expands the data by random, previoulsy un-drawn samples from the training data.
        Generates the output files for EasyChemML.
            1. Generates k random splits of the data set.
            2. Performs stratified sampling from distribution in given target dataset.
            3. Generates a randomly drawn control split of identical dimensionality.
            4. Can perform operations 2 and 3 for different relative sizes of the drawn sample (0 to "max" as max. size)
            5. Expands the training data by previously not drawn samples from the training data.
            6. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            target_dataset (pd.DataFrame): Dataset with the desired distribution of target values.
            target_column (str): Name of the target column in target_dataset
            subset (list): Sampling from "train", "test" or both
            sizes (list): List of relative sizes of the drawn sample (e.g. [0.2, 0.4, 0.6, 0.8, 1] or [0.5, "max"])
            add_amounts (list): List of relative amounts of additional training data.

        Returns:
            None
        """
        # STEP 1: GENERATION OF RANDOM SPLITS
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)
        target_data = {index: target_dataset.at[index, target_column] for index in target_dataset.index.values}

        for size in sizes:
            for add in add_amounts:
                splits_final = {"experiment": [], "control": []}
                for split in splits:
                    train, train_control = split[0], split[0]
                    test, test_control = split[1], split[1]

                    # STEP 2+3: STRATIFIED SAMPLING + GENERATION OF RANDOMLY SAMPLED CONTROL
                    if "train" in subset:
                        train = sample_distribution_from(self.index_target_dict(split[0]), target_data, 0.1, size)
                    if "test" in subset:
                        test = sample_distribution_from(self.index_target_dict(split[1]), target_data, 0.1, size)
                        test_control = sample_random(test, len(test))

                    # STEP 5: ADD ADDITIONAL, RANDOMLY SAMPLED DATA POINTS FROM THE REMAINING DISTRIBUTION
                    to_add = int(add*len(train))
                    not_sampled = list(set(split[0])-set(train))
                    train = train + sample_random(not_sampled, to_add)
                    train_control = sample_random(split[0], len(train))

                    # STEP 6: SAVE SPLITS FOR ML COMPUTATIONS
                    splits_final["experiment"].append((train, test))
                    splits_final["control"].append((train_control, test_control))

                self.save_splits_for_ml(splits_final["experiment"], f"stratified_sampling_{size}_add_random_{add}")
                self.save_splits_for_ml(splits_final["control"], f"stratified_sampling_{size}_add_random_{add}_control")

    def split_sample_add_random_zeros(self, n_splits, split_ratio, target_dataset, target_column, subset, sizes, add_amounts):
        """Performs stratified sampling on random splits of the data set.
        Expands the data by random, previoulsy un-drawn samples from the training data. Targets are set to zero for this data.
        Generates the output files for EasyChemML.
            1. Generates k random splits of the data set.
            2. Performs stratified sampling from distribution in given target dataset.
            3. Generates a randomly drawn control split of identical dimensionality.
            4. Can perform operations 2 and 3 for different relative sizes of the drawn sample (0 to "max" as max. size)
            5. Expands the training data by previously not drawn samples from the training data.
            6. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            target_dataset (pd.DataFrame): Dataset with the desired distribution of target values.
            target_column (str): Name of the target column in target_dataset
            subset (list): Sampling from "train", "test" or both
            sizes (list): List of relative sizes of the drawn sample (e.g. [0.2, 0.4, 0.6, 0.8, 1] or [0.5, "max"])
            add_amounts (list): List of relative amounts of additional training data.

        Returns:
            None
        """
        # STEP 1: GENERATION OF RANDOM SPLITS
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)
        target_data = {index: target_dataset.at[index, target_column] for index in target_dataset.index.values}

        for size in sizes:
            for add in add_amounts:
                splits_final = {"experiment": [], "control": [], "fixed_data": []}
                for split in splits:
                    train, train_control = split[0], split[0]
                    test, test_control = split[1], split[1]

                    # STEP 2+3: STRATIFIED SAMPLING + GENERATION OF RANDOMLY SAMPLED CONTROL
                    if "train" in subset:
                        train = sample_distribution_from(self.index_target_dict(split[0]), target_data, 0.1, size)
                    if "test" in subset:
                        test = sample_distribution_from(self.index_target_dict(split[1]), target_data, 0.1, size)
                        test_control = sample_random(test, len(test))

                    # STEP 5: ADD ADDITIONAL, RANDOMLY SAMPLED DATA POINTS FROM THE REMAINING DISTRIBUTION
                    to_add = int(add*len(train))
                    not_sampled = list(set(split[0])-set(train))
                    train_final = train + sample_random(not_sampled, to_add)
                    train_final_control = sample_random(split[0], len(train_final))

                    # STEP 6: SAVE SPLITS FOR ML COMPUTATIONS
                    splits_final["experiment"].append((train_final, test))
                    splits_final["control"].append((train_final_control, test_control))
                    splits_final["fixed_data"].append(train)

                self.save_splits_for_ml(splits_final["experiment"], f"stratified_sampling_{size}_add_random_zeros_{add}", modify_targets=lambda x: 0, fixed_data=splits_final["fixed_data"])
                self.save_splits_for_ml(splits_final["control"], f"stratified_sampling_{size}_add_random_zeros_{add}_control")

    def split_sample_oversample(self, n_splits, split_ratio, target_dataset, target_column, subset, sizes, add_amounts):
        """Performs stratified sampling on random splits of the data set.
        Expands the data by random oversampling from the training dataset.
        Generates the output files for EasyChemML.
            1. Generates k random splits of the data set.
            2. Performs stratified sampling from distribution in given target dataset.
            3. Generates a randomly drawn control split of identical dimensionality.
            4. Can perform operations 2 and 3 for different relative sizes of the drawn sample (0 to "max" as max. size)
            5. Expands the training data by random oversampling from the training data.
            6. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            target_dataset (pd.DataFrame): Dataset with the desired distribution of target values.
            target_column (str): Name of the target column in target_dataset
            subset (list): Sampling from "train", "test" or both
            sizes (list): List of relative sizes of the drawn sample (e.g. [0.2, 0.4, 0.6, 0.8, 1] or [0.5, "max"])
            add_amounts (list): List of relative amounts of additional training data.

        Returns:
            None
        """
        # STEP 1: GENERATION OF RANDOM SPLITS
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)
        target_data = {index: target_dataset.at[index, target_column] for index in target_dataset.index.values}

        for size in sizes:
            for add in add_amounts:
                splits_final = {"experiment": [], "control": []}
                for split in splits:
                    train, train_control = split[0], split[0]
                    test, test_control = split[1], split[1]

                    # STEP 2+3: STRATIFIED SAMPLING + GENERATION OF RANDOMLY SAMPLED CONTROL
                    if "train" in subset:
                        train = sample_distribution_from(self.index_target_dict(split[0]), target_data, 0.1, size)
                    if "test" in subset:
                        test = sample_distribution_from(self.index_target_dict(split[1]), target_data, 0.1, size)
                        test_control = sample_random(test, len(test))

                    # STEP 5: ADD ADDITIONAL, RANDOMLY SAMPLED DATA POINTS FROM THE REMAINING DISTRIBUTION
                    to_add = int(add*len(train))
                    train = oversample_from(self.index_target_dict(train), target_data, 0.1, to_add)
                    train_control = sample_random(split[0], len(train))

                    # STEP 6: SAVE SPLITS FOR ML COMPUTATIONS
                    splits_final["experiment"].append((train, test))
                    splits_final["control"].append((train_control, test_control))

                self.save_splits_for_ml(splits_final["experiment"], f"stratified_sampling_{size}_oversampling_random_{add}")
                self.save_splits_for_ml(splits_final["control"], f"stratified_sampling_{size}_oversampling_random_{add}_control")

    def split_sample_oversample_zeros(self, n_splits, split_ratio, target_dataset, target_column, subset, sizes, add_amounts):
        """Performs stratified sampling on random splits of the data set.
        Expands the data by random oversampling from the training dataset.
        Generates the output files for EasyChemML.
            1. Generates k random splits of the data set.
            2. Performs stratified sampling from distribution in given target dataset.
            3. Generates a randomly drawn control split of identical dimensionality.
            4. Can perform operations 2 and 3 for different relative sizes of the drawn sample (0 to "max" as max. size)
            5. Expands the training data by random oversampling from the training data.
            6. Saves the modified train-test splits for input to EasyChemML.

        Parameters:
            n_splits (int): Number of splits
            split_ratio (float): Relative size of the test set
            target_dataset (pd.DataFrame): Dataset with the desired distribution of target values.
            target_column (str): Name of the target column in target_dataset
            subset (list): Sampling from "train", "test" or both
            sizes (list): List of relative sizes of the drawn sample (e.g. [0.2, 0.4, 0.6, 0.8, 1] or [0.5, "max"])
            add_amounts (list): List of relative amounts of additional training data.

        Returns:
            None
        """
        # STEP 1: GENERATION OF RANDOM SPLITS
        splits = k_random_splits(self.all_indices, n_splits, split_ratio)
        target_data = {index: target_dataset.at[index, target_column] for index in target_dataset.index.values}

        for size in sizes:
            for add in add_amounts:
                splits_final = {"experiment": [], "control": []}
                for split in splits:
                    train, train_control = split[0], split[0]
                    test, test_control = split[1], split[1]

                    # STEP 2+3: STRATIFIED SAMPLING + GENERATION OF RANDOMLY SAMPLED CONTROL
                    if "train" in subset:
                        train = sample_distribution_from(self.index_target_dict(split[0]), target_data, 0.1, size)
                    if "test" in subset:
                        test = sample_distribution_from(self.index_target_dict(split[1]), target_data, 0.1, size)
                        test_control = sample_random(test, len(test))

                    # STEP 5: ADD ADDITIONAL, RANDOMLY SAMPLED DATA POINTS FROM THE REMAINING DISTRIBUTION
                    train = oversample_from_single_bin(self.index_target_dict(train), 0.1, add, "min")
                    train_control = sample_random(split[0], len(train))

                    # STEP 6: SAVE SPLITS FOR ML COMPUTATIONS
                    splits_final["experiment"].append((train, test))
                    splits_final["control"].append((train_control, test_control))

                self.save_splits_for_ml(splits_final["experiment"], f"stratified_sampling_{size}_oversampling_zeros_{add}")
                self.save_splits_for_ml(splits_final["control"], f"stratified_sampling_{size}_oversampling_zeros_{add}_control")
