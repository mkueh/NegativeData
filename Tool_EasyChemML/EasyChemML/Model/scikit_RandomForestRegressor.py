from sklearn.ensemble import RandomForestRegressor
from EasyChemML.Utilities.MetricUtilities.Metric import MetricMode
from EasyChemML.Model.Abstract_Model import Abstract_Model
import numpy as np
from EasyChemML.Utilities.Application_env import Application_env

class scikit_RandomForestRegressor(Abstract_Model):
    clf = None

    def __init__ (self, param, log_folder:str, APP_ENV:Application_env):
        super().__init__(APP_ENV)
        self.clf = RandomForestRegressor(**param)

    def set_param(self, param: dict):
        self.clf.set_params(**param)

    def get_param(self) -> dict:
        return self.clf.get_params()

    def fit_and_eval(self, X, y, X_test, y_test):
        self.clf.fit(X, y)

    def predict(self, X):
        return self.clf.predict(X)

    @staticmethod
    def getItemname():
        return "scikit_randomforest_r"

    @staticmethod
    def getMetricMode():
        return MetricMode.regressor

    @staticmethod
    def hasBatchMode():
        return False