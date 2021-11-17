import deepchem as dc
from EasyChemML.Utilities.MetricUtilities.Metric import MetricMode
import numpy as np
from deepchem.data.datasets import NumpyDataset
from EasyChemML.Model.Abstract_Model import Abstract_Model
from EasyChemML.Utilities.Application_env import Application_env

class deepchem_GCNN(Abstract_Model):
    clf = None
    __epoch = 50

    def __init__ (self, param, log_folder:str, APP_ENV:Application_env):
        super().__init__(APP_ENV)
        param['mode'] = 'regression'
        param['n_tasks'] = 1
        self.__epoch = param['nb_epoch']
        self.clf = dc.models.GraphConvModel(**param)

    def set_param(self, param: dict):
        self.clf.set_params(**param)

    def get_param(self) -> dict:
        return self.clf.get_params()

    def fit_and_eval(self, X, y, X_test, y_test):
        for i,item in enumerate(y):
            y[i] = float(item)

        feat = dc.feat.ConvMolFeaturizer()
        data_X = dc.data.data_loader.featurize_smiles_np(np.array(X).flatten(),feat)
        data = NumpyDataset(np.array(data_X),np.array(y))
        metric = [dc.metric.Metric(dc.metric.pearson_r2_score, mode="regression")]
        self.clf.fit(data, self.__epoch)

    def predict(self, X):
        feat = dc.feat.ConvMolFeaturizer()
        data_X = dc.data.data_loader.featurize_smiles_np(np.array(X).flatten(),feat)
        data = NumpyDataset(np.array(data_X),None)
        return self.clf.predict(data)

    @staticmethod
    def getItemname():
        return "deepchem_GCNN_r"

    @staticmethod
    def getMetricMode():
        return MetricMode.regressor

    @staticmethod
    def hasBatchMode():
        return False
