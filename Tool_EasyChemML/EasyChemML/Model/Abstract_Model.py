class Abstract_Model():
    from EasyChemML.Utilities.Application_env import Application_env

    APP_ENV:Application_env

    def __init__(self, APP_ENV):
        self.APP_ENV = APP_ENV

    def get_statement(self):
        return 'No Model Info'

    def set_maximum_core(self, n_jobs):
        raise Exception('not implemented yet')

    def set_param(self, param: dict):
        raise Exception('not implemented yet')

    def get_param(self) -> dict:
        raise Exception('not implemented yet')

    def fit_and_eval(self, X, y, X_test, y_test):
        raise Exception('not implemented yet')

    def predict(self, X):
        raise Exception('not implemented yet')

    @staticmethod
    def getMetricMode():
        raise Exception('not implemented yet')

    @staticmethod
    def hasBatchMode():
        return False

    @staticmethod
    def getItemname():
        return "abstractModel"