from ReactionDataset import ReactionDataset
import os

path_to_example = "{}/{}/".format(os.getcwd(), "Example_Folder")

dataset = ReactionDataset(
    basename="Example",
    path=path_to_example,
    source="Reaxys"
)

dataset.import_data()
dataset.save_state(path_to_example)
