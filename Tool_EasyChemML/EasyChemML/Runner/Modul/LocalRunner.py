import logging, datetime, os, pandas
import numpy as np

from EasyChemML.Runner.Utilities.Job import JobTYP, Job, HyperparameterJob, ModelcalculationJob
from EasyChemML.Runner.Modul.Abstract_Runner import Abstract_Runner
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable

from EasyChemML.Utilities.MetricUtilities.Metric import Metric
from EasyChemML.Utilities.Dataset import Dataset
from EasyChemML.Model.Abstract_Model import Abstract_Model
from EasyChemML.Utilities.Application_env import Application_env

from typing import List


class LocalRunner(Abstract_Runner):
    workingPath: str

    def __init__(self, working_path: str, param: dict, APP_ENV: Application_env):  # TODO param
        super().__init__(APP_ENV)
        self.workingPath = working_path

    def run_Jobs(self, jobs: List[Job]) -> List[Job]:
        tmp = []
        for job in jobs:
            tmp.append(self._run_job(job))
        return tmp

    def _run_job(self, job: Job) -> Metric:
        print(f'run job: {job.job_id}')
        if job.getTyp() is JobTYP.Hyperparameter:
            return self._run_hyperparameterJob(job)
        elif job.getTyp() is JobTYP.Modelcalculation:
            return self._run_ModelJob(job)

    def _run_hyperparameterJob(self, job: HyperparameterJob):
        dataset: Dataset = job.getDataset()

        splits = dataset.getSplits()
        feature = dataset.getFeature_data()
        target = dataset.getTargets_data()

        current_split = splits.get_inner_split_absolut(job.get_outerStepIndex(), job.get_innerStepIndex())

        log_inFolder = os.path.join(self.workingPath, f'OuterCV_{job.config.config_id}_Nested_{job.job_id}_Logfolder')
        clf: Abstract_Model = job.algorithm(job.get_explicit_algorithm_para(), log_inFolder, self.APP_ENV)
        metric = self.APP_ENV.get_Hyperparameter_MetricFabricator().createEmptyMetric()

        logging.info(f'----------! Hyperparameter_Job: {job.job_id} !----------')
        if clf.hasBatchMode() == False:
            X = feature[current_split.train]
            y = target[current_split.train]
            X_test = feature[current_split.test]
            y_test = target[current_split.test]
            clf.fit_and_eval(X=X, y=y, X_test=X_test, y_test=y_test)

            y_predict = clf.predict(X_test)
            metric.calcMetric(y_test, y_predict)
            logging.info(f'----------! Hyperparameter_Job: {job.job_id} is finish !----------')
            logging.info('  ')
            self.__logMetricResults(metric, True)

            job.result_metric = metric
            job.set_finished(True)
        else:
            raise Exception('Batchlearning is not implemented at the moment')

        return job

    def _run_ModelJob(self, job: ModelcalculationJob):
        logging.info('\n\n----------------------------------------------------')
        logging.info('Start the training of the best configuration')
        logging.info('Config: ' + str(job.config.config_id))

        dataset: Dataset = job.getDataset()

        splits = dataset.getSplits()
        feature: BatchTable = dataset.getFeature_data()
        target: BatchTable = dataset.getTargets_data()

        clf: Abstract_Model = job.algorithm(job.get_explicit_algorithm_para(),
                                            os.path.join(self.workingPath, f'OuterCV_{job.config.config_id}_Logfolder'),
                                            self.APP_ENV)

        metricy = self.APP_ENV.get_Output_MetricFabricator().createEmptyMetric()
        metricX = self.APP_ENV.get_Output_MetricFabricator().createEmptyMetric()

        logging.info(str(job.algorithm) + " is started")

        counter = job.config.config_id

        # train_index, test_index = self.splits.out_splits[outer_index]
        current_split = splits.get_outer_split(job.get_outerStepIndex())

        logging.info('Outer-CV-Step ' + str(counter) + ' with best configuration is started')
        logging.info('Time: ' + str(datetime.datetime.now()))

        if clf.hasBatchMode() == False:
            X = feature[current_split.train]
            y = target[current_split.train]
            X_test = feature[current_split.test]
            y_test = target[current_split.test]

            clf.fit_and_eval(X=X, y=y, X_test=X_test, y_test=y_test)

            # Testset Prediction
            y_predict = clf.predict(X_test)
            metricy.calcMetric(y_test, y_predict)

            # Trainset Prediction
            X_predict = clf.predict(X)
            metricX.calcMetric(y, X_predict)

            # Print Testset prediction
            columns_testP = ['True_values', 'Predicted_values']
            columns_testP.extend(metricy.metrics_name)
            arrays = [y_test, y_predict]
            for metric in metricy.metrics_name:
                arrays.append([metricy[metric]])

            self.__exportToCSV(arrays=arrays,
                               columns_a=columns_testP,
                               path=self.workingPath,
                               CSV_filename=('Outer_Step_' + str(counter) + '_Testprediction.csv'))

            # Print Trainset prediction
            columns_trainP = ['True_values', 'Predicted_values']
            columns_trainP.extend(metricX.metrics_name)
            arrays = [y, X_predict]
            for metric in metricX.metrics_name:
                arrays.append([metricX[metric]])

            self.__exportToCSV(arrays=arrays,
                               columns_a=columns_trainP,
                               path=self.workingPath,
                               CSV_filename=('Outer_Step_' + str(counter) + '_Trainprediction.csv'))
            logging.info('Outer-CV-Step is finished')
            self.__logMetricResults(metricy, False)

            job.result_metricy = metricy
            job.result_metricX = metricX
            job.set_finished(True)

        else:
            raise Exception('Batchlearning is not implemented at the moment')

        return job

    def __exportToCSV(self, arrays: [], columns_a: [str], path, CSV_filename):
        DataContainer = {}
        maxsize = self.__lagestArray(ars=arrays)

        i = 0
        for c in columns_a:
            arrays[i] = list(arrays[i])
            if len(arrays[i]) < maxsize:
                arrays[i].extend([''] * (maxsize - len(arrays[i])))
            DataContainer[c] = arrays[i]
            i = i + 1

        dataFrame_results = pandas.DataFrame(DataContainer)
        dataFrame_results.to_csv(os.path.join(path, CSV_filename), header=True, index=False)

    def __lagestArray(self, ars: []):
        max_size = -1

        for arr in ars:
            try:
                tmp_arr = list(arr)
            except:
                continue

            if isinstance(tmp_arr, list) and max_size < len(tmp_arr):
                max_size = len(tmp_arr)
        return max_size

    def __logMetricResults(self, metric: Metric, inner):
        logging.info('.............! Results !.............')
        if inner:
            logging.info('Results of the Hyperparameter-Job run:')
        else:
            logging.info('Results of the Outer-Job run:')
        for item in metric.metrics_name:
            logging.info(item + ': ' + str(np.average(metric[item])))
        logging.info('Time: ' + str(datetime.datetime.now()))
        logging.info('---------------------------------------------------')

    @staticmethod
    def getItemname():
        return "local_runner"
