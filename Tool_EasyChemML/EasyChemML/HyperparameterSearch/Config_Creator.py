from EasyChemML.Utilities.Dataset import Dataset
from EasyChemML.Utilities.DatasetHolder import DatasetHolder
from EasyChemML.Utilities.Application_env import Application_env
from EasyChemML.HyperparameterSearch.Utilities.Config import Config
from EasyChemML.HyperparameterSearch.Utilities.HyperParamter import HyperParameter
from typing import Dict


class Config_Creator(object):
    """
    Create hyperparameter configurations

    For each Hyperparamter, outersplit and innersplit a configuation is created
    """

    APP_ENV: Application_env

    def __init__(self, APP_ENV: Application_env):
        self.APP_ENV = APP_ENV

    def _load_Hyperparameter(self, parameters: Dict):
        args = {}
        containHyperparameter = False

        for para in parameters:
            if isinstance(parameters[para], dict):
                args[para] = HyperParameter(parameters[para])
                containHyperparameter = True
            else:
                args[para] = parameters[para]
        return args, containHyperparameter

    def createConfigurations(self, datasetholder: DatasetHolder, algorithm_name:str, algorithm_para:dict):
        configs = []

        args, containHyperparameter = self._load_Hyperparameter(algorithm_para)
        algorithm = self.APP_ENV.get_ModulManager().get_model(algorithm_name)

        if datasetholder.splitted:
            for i in range(len(datasetholder)):
                dataset = datasetholder[i]
                configs.append(Config(f'{i}', dataset, 0, algorithm, args, containHyperparameter))
        else:
            for i in range(datasetholder[0].getSplits().get_outerCount()):
                configs.append(Config(f'{i}', datasetholder[0], i, algorithm, args, containHyperparameter))

        return configs
