from EasyChemML.Utilities.Dataset import Dataset
from EasyChemML.Model.Abstract_Model import Abstract_Model

from typing import Dict

class Config(object):
    config_id:str

    algorithm:Abstract_Model = -1
    implicit_algorithm_para:Dict = -1

    data:Dataset = None
    outer_index = -1

    containHyperparameter:bool = False


    def __init__(self, config_id:str, data:Dataset, outer_index, algorithm:Abstract_Model, implicit_algorithm_para:Dict, containHyperparameter=False):
        self.algorithm = algorithm
        self.implicit_algorithm_para = implicit_algorithm_para
        self.data = data
        self.containHyperparameter = containHyperparameter
        self.outer_index = outer_index
        self.config_id = config_id
