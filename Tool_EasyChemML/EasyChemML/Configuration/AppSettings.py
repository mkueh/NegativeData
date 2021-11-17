from typing import List, Dict


class AppSettings(object):
    workingPath: str

    Input_featureType: int
    Input_targetType: int

    Input_featurePath: str
    Input_featureColume: List[str]
    Input_featureColumeEncoding: List[str]
    Input_featureImportSettings: Dict

    Input_targetPath: str
    Input_targetColume: List[str]
    Input_targetImportSettings: Dict

    Additional_Datapayload:Dict

    Encoder: str
    Encoder_settings: Dict

    Preprocessing_feature_Steps: List[str]
    Preprocessing_feature_Steps_param: List[Dict]

    Preprocessing_target_Steps: List[str]
    Preprocessing_target_Steps_param: List[Dict]

    HyperparamterSearch: str
    HyperparamterSearch_settings: Dict
    Fixparam_forOuter: Dict

    Jobrunner: str
    Jobrunner_settings: Dict

    Model_algo: List[str]
    Model_algoSettings: List[dict]

    Splitter_innerSplitter: str
    Splitter_innerSettings: Dict
    Splitter_outerSplitter: str
    Splitter_outerSettings: Dict
    Splitter_saveLoadSplit: str

    Output_metrics: List[str]
    Output_metrics_settings: List
    Hyperparamter_metric: str
    Hyperparamter_setting: Dict

    Validation_runOnehot: int

    System_chunksize: int
