from EasyChemML.Utilities.Application_env import Application_env
from typing import List

class EncoderInterface(object):
    APP_ENV:Application_env

    def __init__(self, APP_ENV:Application_env):
        self.APP_ENV = APP_ENV

    def convert(self, dataset, columns:List[str], n_jobs: int, **kwargs):
        pass #set dataset and return databuffer

    @staticmethod
    def convert_foreach_outersplit():
        return False

    @staticmethod
    def is_parallel():
        return False

    @staticmethod
    def getItemname():
        return "notuseit"