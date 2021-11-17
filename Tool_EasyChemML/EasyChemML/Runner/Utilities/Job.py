from enum import Enum, auto

import copy

from EasyChemML.Model.Abstract_Model import Abstract_Model
from EasyChemML.HyperparameterSearch.Config_Creator import Config
from EasyChemML.Utilities.Dataset import Dataset
from EasyChemML.Utilities.MetricUtilities.Metric import Metric

from typing import Dict
from abc import ABC, abstractmethod


class JobTYP(Enum):
    Hyperparameter = auto()
    Modelcalculation = auto()


class Job(ABC):
    job_id: int

    algorithm: Abstract_Model = None
    _explicit_algorithm_para: Dict = None

    finished = False

    def __init__(self, job_id:int, algorithm: Abstract_Model, explicit_algorithm_para):
        self.job_id = job_id
        self.algorithm = algorithm
        self._explicit_algorithm_para = explicit_algorithm_para

    def get_explicit_algorithm_para(self):
        return copy.deepcopy(self._explicit_algorithm_para)

    def getDataset(self) -> Dataset:
        return self.config.data

    def getTyp(self) -> JobTYP:
        pass

    def isfinished(self):
        return self.finished

    def set_finished(self, finished: bool):
        self.finished = finished


class HyperparameterJob(Job):
    config: Config
    _inner_Step = None
    result_metric:Metric


    def __init__(self, job_id, algorithm: Abstract_Model, explicit_algorithm_para, config: Config, inner_Step: int):
        super().__init__(job_id, algorithm, explicit_algorithm_para)
        self.config = config
        self._inner_Step = inner_Step

    def __repr__(self):
        return f'HyperJOB: JobID:' + str(self.job_id) + ' | Config: ' + str(self.config.config_id) + ' | Outer_Step: ' + str(self.config.outer_index) + ' | Inner_Step: ' + str(self.inner_Step)

    def getTyp(self):
        return JobTYP.Hyperparameter

    def get_innerStepIndex(self):
        return self._inner_Step

    def get_outerStepIndex(self):
        return self.config.outer_index

    def set_resultMetric(self, metric:Metric):
        self.result_metric = metric


class ModelcalculationJob(Job):
    config: Config

    result_metricX:Metric
    result_metricy:Metric

    def __init__(self, job_id, algorithm: Abstract_Model, explicit_algorithm_para, config: Config):
        super().__init__(job_id, algorithm, explicit_algorithm_para)
        self.config = config

    def __repr__(self):
        return 'ModelJOB: JobID: ' + str(self.job_id) + ' | Config: ' + str(self.config.config_id) + ' | Outer_Step: ' + str(self.config.outer_index)

    def get_outerStepIndex(self):
        return self.config.outer_index

    def getTyp(self):
        return JobTYP.Modelcalculation

    def set_resultMetric(self, metricX:Metric, metricy:Metric):
        self.result_metricX = metricX
        self.result_metricy = metricy
