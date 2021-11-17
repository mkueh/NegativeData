


class MetricFabricator():
    __slots__ = ['metrics_paras', 'metrics_names']

    def __init__(self, metrics_names, metrics_paras):
        self.metrics_paras = metrics_paras
        self.metrics_names = metrics_names

    def createEmptyMetric(self, calcmetrics_dict=None, metrics_names=None, metrics_paras=[]):
        from .Metric import MetricMode, Metric
        if self.metrics_paras == -1 or self.metrics_names == -1:
            raise Exception('MetricFabricator has not been initialized')

        if metrics_names is None and metrics_paras == []:
            return Metric(metrics=self.metrics_names, metrics_para=self.metrics_paras, MFabricator=self,
                          calcmetrics_dict=calcmetrics_dict)

        elif not metrics_names is None and metrics_paras == []:
            return Metric(metrics=self.metrics_names, metrics_para=[], calcmetrics_dict=calcmetrics_dict,
                          MFabricator=self)

        elif metrics_names is None:
            raise Exception('metrics_names is None, but metrics_paras is not None')
