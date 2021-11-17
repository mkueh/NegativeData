from .Abstract_Hyperparametersearch import Abstract_Hyperparametersearch

from typing import List, Dict
from hyperopt import hp, fmin, tpe, STATUS_OK, Trials
from hyperopt.pyll.base import scope

from EasyChemML.HyperparameterSearch.Utilities.Config import Config
from EasyChemML.HyperparameterSearch.Utilities.HyperParamter import HyperParameter, HyparameterTyp
from EasyChemML.HyperparameterSearch.Utilities.HyperParamter import IntRange, FloatRange, Categorically
from EasyChemML.Runner.Utilities.Job import HyperparameterJob

from EasyChemML.Utilities.MetricUtilities.MetricList import MetricList
from EasyChemML.Utilities.MetricUtilities.Metric import Metric, MetricDirection
from EasyChemML.Utilities.MetricUtilities.MetricFabricator import MetricFabricator
from EasyChemML.Utilities.Application_env import Application_env

from EasyChemML.Runner.Modul.LocalRunner import LocalRunner

import numpy as np

class Hyperopt(Abstract_Hyperparametersearch):

    #TODO add the other hyperparameter distributions

    _eval_type = ''
    _working_path = ''
    _max_evals = 10
    _counter = 0

    def __init__(self, eval_type, working_path, APP_ENV:Application_env ,kwargs):
        super().__init__(APP_ENV)
        if isinstance(eval_type, list) or isinstance(eval_type, np.ndarray):
            if len(eval_type) > 1:
                raise Exception('Hyperopt can optimize only one metric')
            else:
               self._eval_type = eval_type[0]
        else:
            self._eval_type = eval_type
        self._working_path = working_path

        if 'max_evals' in kwargs:
            self._max_evals = int(kwargs['max_evals'])


    def performe_HyperparamterSearch(self, configs: List[Config], runner: LocalRunner) -> Dict[Config, Dict]:
        self._MFabricator = self.APP_ENV.get_Hyperparameter_MetricFabricator()

        out_list = {}
        for c in configs:
            out_list[c] = {}

            parameter = self._convertHyperparamert2Hyperopt(c, runner)
            trials = Trials()
            best = fmin(self._minimize2Funktion, space=parameter, algo=tpe.suggest, max_evals=self._max_evals, trials=trials)
            out_list[c]['best_param'] = self._convertHyperopt2explicit(c, best)
            out_list[c]['metric'] = trials.best_trial['result']['metric']
        return out_list

    def _minimize2Funktion(self, parameter:Dict):
        config, runner = parameter['hyperopt_Bypass']
        del parameter['hyperopt_Bypass']
        runner:LocalRunner

        jobs = []
        for inner in range(config.data.getSplits().get_innerCount(config.outer_index)):
            jobs.append(HyperparameterJob(f'Job_{self._counter}', config.algorithm, parameter, config, inner))
            self._counter += 1

        finished_jobs = runner.run_Jobs(jobs)

        metrics = MetricList()

        for i,job in enumerate(finished_jobs):
            metrics + job.result_metric

        avarage = metrics.calcAverage()

        if Metric.getbestdirection(self._eval_type) == MetricDirection.higherIsbetter:
            if self._eval_type in Metric.gethigherIsBetter():
                return {'loss': 1-avarage[self._eval_type], 'status': STATUS_OK, 'metric': avarage}
            else:
                raise Exception(f'{self._eval_type} is not supported by Hyperopt at the moment')
        else:
            return {'loss': avarage[self._eval_type], 'status': STATUS_OK, 'metric':avarage }


    def _convertHyperopt2explicit(self, config:Config, hyperopt_para:Dict):
        parameters = config.implicit_algorithm_para

        converted_para = {}

        for para in parameters:
            entry = parameters[para]
            if isinstance(entry, HyperParameter):
                htyp = entry.getTyp()

                if htyp == HyparameterTyp.Int_range:
                    entry:IntRange = entry.getHyperparamter()
                    converted_para[para] = int(hyperopt_para[para])
                elif htyp == HyparameterTyp.Float_range:
                    entry:FloatRange = entry.getHyperparamter()
                    converted_para[para] = hyperopt_para[para]
                elif htyp == HyparameterTyp.Categorical:
                    entry:Categorically = entry.getHyperparamter()
                    converted_para[para] = hyperopt_para[para]
                else:
                    raise Exception(f'found a new Hyperparamtertyp that is not supported: {htyp}')
            else:
                converted_para[para] = parameters[para]
        return converted_para

    def _convertHyperparamert2Hyperopt(self, config:Config, runner):
        parameters = config.implicit_algorithm_para

        converted_para = {}
        converted_para['hyperopt_Bypass'] = (config,runner)

        for para in parameters:
            entry = parameters[para]
            if isinstance(entry, HyperParameter):
                htyp = entry.getTyp()

                if htyp == HyparameterTyp.Int_range:
                    entry:IntRange = entry.getHyperparamter()
                    converted_para[para] = scope.int(hp.quniform(para, int(entry.start), int(entry.end), 1))
                elif htyp == HyparameterTyp.Float_range:
                    entry:FloatRange = entry.getHyperparamter()
                    converted_para[para] = hp.uniform(para, entry.start, entry.end)
                elif htyp == HyparameterTyp.Categorical:
                    entry:Categorically = entry.getHyperparamter()
                    converted_para[para] = hp.choice(para, entry.items)
                else:
                    raise Exception(f'found a new Hyperparamtertyp that is not supported: {htyp} - at {para}')
            else:
                converted_para[para] = parameters[para]
        return converted_para

    @staticmethod
    def getItemname():
        return "hyperopt"