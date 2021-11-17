import copy, os, csv
from typing import List, Dict

from EasyChemML.HyperparameterSearch.Utilities.Config import Config
from EasyChemML.HyperparameterSearch.Utilities.HyperParamter import HyperParameter
from EasyChemML.Runner.Utilities.Job import HyperparameterJob
from .Abstract_Hyperparametersearch import Abstract_Hyperparametersearch

from EasyChemML.Runner.Modul.LocalRunner import LocalRunner

from EasyChemML.Utilities.MetricUtilities.MetricList import MetricList
from EasyChemML.Utilities.MetricUtilities.Metric import Metric, MetricDirection
from EasyChemML.Utilities.MetricUtilities.MetricFabricator import MetricFabricator
from EasyChemML.Utilities.Application_env import Application_env


class GridSearch(Abstract_Hyperparametersearch):
    _eval_type = ''
    _working_path = ''
    _MFabricator:MetricFabricator

    def __init__(self, eval_type, working_path, APP_ENV:Application_env ,kwargs):
        super().__init__(APP_ENV)
        if isinstance(eval_type, list):
            self._eval_type = eval_type[0]
        else:
            self._eval_type = eval_type
        self._working_path = working_path

    def performe_HyperparamterSearch(self, configs: List[Config], runner: LocalRunner) -> Dict[
        Config, HyperparameterJob]:
        print('Grid search will be initialized')

        self._MFabricator = self.APP_ENV.get_Hyperparameter_MetricFabricator()

        all_jobs = []
        zuordnung = {}
        for c in configs:
            tmp_jobs, jobsZuordnung = self.__generateJobs(c)
            all_jobs.extend(tmp_jobs)
            zuordnung[c] = jobsZuordnung
        print('Jobs created')

        jobs = runner.run_Jobs(all_jobs)

        return self._create_output(zuordnung,configs)

    def _create_output(self, zuordnung:Dict[Config, Dict], configs: List[Config]):
        out_list = {}

        for c in configs:
            results = zuordnung[c]
            for result in results:
                size = len(result['jobs'])
                metriclist = MetricList()

                for i, job in enumerate(result['jobs']):
                    metriclist + job.result_metric

                result['final_score'] = metriclist.calcAverage()

        for c in configs:
            out_list[c] = {}
            if Metric.getbestdirection(self._eval_type) == MetricDirection.higherIsbetter:
                tmp_list = zuordnung[c]
                tmp_list.sort(key=lambda x: x['final_score'][self._eval_type], reverse=True)
            else:
                tmp_list = zuordnung[c]
                tmp_list.sort(key=lambda x: x['final_score'][self._eval_type], reverse=False)
            out_list[c]['best_param'] = tmp_list[0]['para']
            out_list[c]['metric'] = tmp_list[0]['final_score']

        return out_list


    def _parameter2CSV(self, path):
        w = csv.writer(open(os.path.join(path, "ParameterSet.csv"), "w"))
        w.writerow(['ID', 'Klassifizierer', 'Parameter', 'featureSubset'])

    def __generateJobs(self, config: Config) -> List[HyperparameterJob]:
        parameters = config.implicit_algorithm_para

        paraSet = {}
        for parameter in parameters:
            if isinstance(parameters[parameter], HyperParameter):
                val: HyperParameter = parameters[parameter]
                paraSet[parameter] = val.generateExplicitList()
            else:
                paraSet[parameter] = [parameters[parameter]]

        param_permutation = [{}, ]
        for k, v in paraSet.items():
            new_values = len(v)
            current_exp_len = len(param_permutation)
            for _ in range(new_values - 1):
                param_permutation.extend(copy.deepcopy(param_permutation[:current_exp_len]))
            for validx in range(len(v)):
                for exp in param_permutation[validx * current_exp_len:(validx + 1) * current_exp_len]:
                    exp[k] = v[validx]

        jobs = []
        jobsZuordnung = []
        counter = 0
        for i, param_set in enumerate(param_permutation):
            jobsZuordnung.append({})
            jobsZuordnung[i]['para'] = param_set
            jobsZuordnung[i]['jobs'] = []
            for inner in range(config.data.getSplits().get_innerCount(config.outer_index)):
                job = HyperparameterJob(f'{counter}', config.algorithm, param_set, config, inner)
                jobsZuordnung[i]['jobs'].append(job)
                jobs.append(job)
                counter += 1


        return jobs, jobsZuordnung

    @staticmethod
    def getItemname():
        return "grid_search"
