from sklearn.metrics import mean_squared_error, r2_score, explained_variance_score, max_error, mean_squared_log_error, \
    mean_absolute_error

from enum import Enum, auto
from .Metric import Metric, MetricMode
from itertools import repeat
import numpy as np
import csv, copy, sys
from .MetricFabricator import MetricFabricator

from typing import List


class MetricList(object):
    metrics: List[Metric] = -1

    def __init__(self):
        self.metrics = []

    def __getitem__(self, index):
        return self.metrics[index]

    def __add__(self, other: Metric):
        if isinstance(other, Metric):
            if len(self.metrics) > 0:
                if self.metrics[0].equalConfig(other):
                    self.metrics.append(other)
                else:
                    raise Exception('It is not possible to add a Metric with a different metricset to the metric list')
            else:
                self.metrics.append(other)
        else:
            raise Exception('Cant add a none Metric-Type to MetricList')
        return self

    def __delitem__(self, index):
        del self.metrics[index]

    def __len__(self):
        return len(self.metrics)

    def calcAverage(self) -> Metric:
        avarage_dict = {}

        if len(self.metrics) > 0:
            possiblemetrics = self.metrics[0].metrics_name

            for metric_name in possiblemetrics:
                listofValues = []
                for metric in self.metrics:
                    listofValues.append(metric[metric_name])

                avarage_dict[metric_name] = np.average(listofValues)

            return self.metrics[0].get_MetricFabricator().createEmptyMetric(avarage_dict)
        else:
            raise Exception('The MetricList ist empty')

    def getbestMetric(self, eval_Type):
        value = 0
        best_index = 0
        for index, m in enumerate(self.metrics):
            if index == 0:
                value = self.metrics[index][eval_Type]
                best_index = index
            else:
                if not eval_Type in Metric.getlowerIsBetter():
                    if value < self.metrics[index][eval_Type]:
                        value = self.metrics[index][eval_Type]
                        best_index = index
                else:
                    if value > self.metrics[index][eval_Type]:
                        value = self.metrics[index][eval_Type]
                        best_index = index
        return self.metrics[best_index]

    def saveMetricAsCSV(self, path):
        with open(path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            ava_metric = self.calcAverage()

            writer.writerow(['Average'])
            writer.writerow([k for k in ava_metric])
            writer.writerow([v for v in ava_metric.values()])

            writer.writerow(['Steps'])

            writer.writerow(['NR.'] + [k for k in ava_metric])

            for i, m in enumerate(self.metrics):
                rowList = [str(i)]
                for value in m.values():
                    rowList.append(value)
                writer.writerow(rowList)
