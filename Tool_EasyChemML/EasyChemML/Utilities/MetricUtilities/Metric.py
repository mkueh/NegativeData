# regressor metrics
from sklearn.metrics import mean_squared_error, r2_score, explained_variance_score, max_error, mean_absolute_error
# classifier metrics
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score, hamming_loss, \
    jaccard_score, log_loss, matthews_corrcoef, precision_score, recall_score, zero_one_loss

from enum import Enum, auto
from typing import List, Dict
from .MetricFabricator import MetricFabricator


class MetricMode(Enum):
    classifier = 'c'
    regressor = 'r'


class MetricDirection(Enum):
    higherIsbetter = 'h'
    lowerIsbetter = 'l'


class Metric(object):
    metric:Dict = -1

    metrics_name: List[str]
    metrics_para: List[Dict]
    _MFabricator: MetricFabricator


    def __init__(self, metrics:List[str], metrics_para:List[Dict], MFabricator:MetricFabricator, calcmetrics_dict = None):
        self.metrics_name = metrics
        self.metrics_para = metrics_para
        self._MFabricator = MFabricator

        #check if parameter are okay
        if not len(self.metrics_para) == len(self.metrics_name):
            for i, _ in enumerate(self.metrics_name):
                self.metrics_para.append({})

            if not len(self.metrics_para) == len(self.metrics_name):
                raise Exception('something is wrong with the parameter')

        #check if metric is in mixed mode -- not recommended

        l_regressor = Metric.getpossibleMetrics(MetricMode.regressor)
        l_class = Metric.getpossibleMetrics(MetricMode.classifier)
        regres = False
        for name in self.metrics_name:
            if name in l_regressor:
                regres = True
            elif name in l_class:
                if regres == True:
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                    print('Metric is in mixed mode because a regressor and a classifier metric is selected')
                    print('this is not recommended because some metrics can not process continuous values')
                    print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')


        if calcmetrics_dict is None:
            self.metric = {}
            for name in self.metrics_name:
                if name in self.getpossibleMetrics():
                    self.metric[name] = None
                else:
                    raise Exception(f'Metricname: {name} is not supported')

        else:
            #create a calculated metric holder
            if self._check_metric_dict(calcmetrics_dict):
                self.metric = calcmetrics_dict
            else:
                raise Exception('The given metric_dict is not correct and can not fit in the metric-class')

    def __repr__(self):
        string = ''
        for i, name in enumerate(self.metrics_name):
            if i == 0:
                string = f'{name}: {self.metric[name]}'
            else:
                string = string + f' | {name}: {self.metric[name]}'
        return string

    def __getitem__(self, item):
        return self.metric[item]

    def __iter__(self):
        return self.metric.__iter__()

    def get_MetricFabricator(self):
        return self._MFabricator

    def equalConfig(self, metric):

        def dict_equal(dict_1, dict_2):
            shared_items = {k: dict_1[k] for k in dict_1 if k in dict_2 and dict_1[k] == dict_2[k]}
            if len(shared_items) == len(dict_1):
                return True
            return False

        if isinstance(metric, Metric):
            if len(metric.metrics_name) != len(self.metrics_name) and len(metric.metrics_para) != len(self.metrics_para):
                return False
            bool_name = metric.metrics_name == self.metrics_name
            bool_para = metric.metrics_para == self.metrics_para

            if bool_name and bool_para:
                return True
        else:
            raise Exception('Param metric is not an Metric-object')

    def values(self):
        return self.metric.values()

    def keys(self):
        return self.metric.keys()

    def _check_metric_dict(self, metric_dict:Dict) -> bool:
        possibles = self.metrics_name
        if len(metric_dict) == len(possibles):
            for p_name in possibles:
                if not p_name in metric_dict:
                    print(f'{p_name} is not in metric_dict')
                    return False
            return True
        else:
            print(f'metric_dict contains keys that are not supported')
            return False


    def calcMetric(self, y_true, y_predict):
            for i, name in enumerate(self.metrics_name):
                self.metric[name] = self._calcMetric(name, y_true, y_predict, param=self.metrics_para[i])


    def _calcMetric(self, name, y_true, y_predict, param):
        if name == 'r2_score':
            return r2_score(y_true, y_predict, **param)

        elif name == 'mean_squared_error':
            return mean_squared_error(y_true, y_predict, **param)

        elif name == 'mean_absolute_error':
            return mean_absolute_error(y_true, y_predict, **param)

        elif name == 'explained_variance_score':
            return explained_variance_score(y_true, y_predict, **param)

        elif name == 'max_error':
            return max_error(y_true, y_predict, **param)

        elif name == 'accuracy_score':
            return accuracy_score(y_true, y_predict, **param)

        elif name == 'f1_score':
            return f1_score(y_true, y_predict, **param)

        elif name == 'hamming_loss':
            return hamming_loss(y_true, y_predict, **param)

        elif name == 'jaccard_score':
            return jaccard_score(y_true, y_predict, **param)

        elif name == 'precision_score':
            return precision_score(y_true, y_predict, **param)

        elif name == 'recall_score':
            return recall_score(y_true, y_predict, **param)

        elif name == 'zero_one_loss':
            return zero_one_loss(y_true, y_predict, **param)

        else:
            raise Exception(f'Metricname: {name} is not supported')

    @staticmethod
    def getpossibleMetrics(metric_mode: MetricMode = None):
        """
        metric_mode: default you get metrics of all type
        """
        if metric_mode is None:
            l_regressor = Metric.getpossibleMetrics(MetricMode.regressor)
            l_class= Metric.getpossibleMetrics(MetricMode.classifier)
            l_regressor.extend(l_class)
            return l_regressor
        elif metric_mode == MetricMode.regressor:
            return ['r2_score', 'mean_squared_error', 'mean_absolute_error', 'explained_variance_score', 'max_error']
        elif metric_mode == MetricMode.classifier:
            return ['accuracy_score', 'f1_score_micro', 'f1_score_macro', 'f1_score_weighted', 'hamming_loss',
                    'jaccard_score_micro', 'jaccard_score_macro', 'jaccard_score_weighted',
                    'precision_score_micro', 'precision_score_macro', 'precision_score_weighted', 'recall_score_micro',
                    'recall_score_macro', 'recall_score_weighted', 'zero_one_loss']

    @staticmethod
    def gethigherIsBetter():
        higherIsBetter = ['r2_score', 'explained_variance_score', 'accuracy_score', 'f1_score_micro', 'f1_score_macro',
                          'f1_score_weighted',
                          'precision_score_micro', 'precision_score_macro', 'precision_score_weighted',
                          'recall_score_micro',
                          'recall_score_macro', 'recall_score_weighted', ]
        return higherIsBetter

    @staticmethod
    def getlowerIsBetter():
        lowerIsBetter = ['mean_squared_error', 'mean_absolute_error', 'max_error', 'hamming_loss', 'zero_one_loss']
        return lowerIsBetter

    @staticmethod
    def getbestdirection(metricName: str) -> MetricDirection:
        higherIsBetter = Metric.gethigherIsBetter()
        lowerIsBetter = Metric.getlowerIsBetter()

        if metricName in higherIsBetter:
            return MetricDirection.higherIsbetter
        elif metricName in lowerIsBetter:
            return MetricDirection.lowerIsbetter

        raise Exception(f'Metricname {metricName} is not supported by the metric object')

    @staticmethod
    def getMetricTyp(metricName: str):
        if metricName in Metric.getpossibleMetrics(MetricMode.regressor):
            return MetricMode.regressor
        elif metricName in Metric.getpossibleMetrics(MetricMode.classifier):
            return MetricMode.classifier
