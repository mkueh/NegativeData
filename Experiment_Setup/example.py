from prepare_experiments import SamplingExperiments
import pandas as pd

##################################################################################
### Example Sheet for Setting up Sampling Experiments on Experimental Datasets ###
##################################################################################

# Example: Dataset from Doyle, Dreher et al. (Science 2018) - saved in "Example_Folder"
# Definition of properties and required metadata
raw_data_path = "Example_Folder/Source_Data"
basename = "Doyle_Science_2018"
data_types = {
    "Aniline": "smiles",
    "Aryl Halide": "smiles",
    "Ligand": "smiles",
    "Base": "smiles",
    "Additive": "smiles",
    "Product": "smiles",
    "Yield": "float"
}
target = "Yield"
destination = "."

# Instantiation of the Experiment Generator
exp_generator = SamplingExperiments(raw_data_path, basename, data_types, target, destination)

# Generation of 10 Random 70/30 Splits
exp_generator.random_splits(
    n_splits=10,
    split_ratio=0.3
)

# Generation of 10 Random 70/30 Splits, Followed by Stratified Sampling from a Dataset with Literature Yield Distribution
# Stratified sampling is performed only on the train dataset, using 20%, 40%, ..., 100% of the max. sample size.
# For copyright reasons, the Literature Dataset in this Example is not a real, full dataset from the Literature.
destination_dataset = pd.read_csv("Example_Folder/Literature_Data/Dummy_Dataset.csv", sep="\t", header=0, index_col=0)
exp_generator.split_sample(
    n_splits=10,
    split_ratio=0.3,
    target_dataset=destination_dataset,
    target_column="Yield",
    subset=["train"],
    sizes=[0.2*i for i in range(1, 6)]
)

# Generation of 10 Random 70/30 Splits, Followed by Stratified Sampling and Data Expansion by Oversampling
# Stratified sampling is performed only on the train dataset using the max. sample size.
# Oversampling is performed on the training dataset, expanding it by 20%, 40%, ... 200% of its original size.
exp_generator.split_sample_oversample(
    n_splits=10,
    split_ratio=0.3,
    target_dataset=destination_dataset,
    target_column="Yield",
    subset=["train"],
    sizes=["max"],
    add_amounts=[0.2*i for i in range(1, 11)]
)
