###########################################################
### Example Sheet for Importing and Processing Datasets ###
###########################################################

from ReactionDataset import ReactionDataset

# Set the path to the folder where the Import Settings and the Raw Data are located.
# See ReactionDataset.py for further details on format.
# For copyright reasons, the dataset in this example is not a real, full dataset from the Literature.
path_to_example = "Example_Folder"

# Instantiate the ReactionDataset class.
dataset = ReactionDataset(
    basename="Example",
    path=path_to_example,
    source="Reaxys"
)

# Perform Data Import and Cleaning.
dataset.import_data()

# Save the Processed Dataset and corresponding metadata.
dataset.save_state(path_to_example)
