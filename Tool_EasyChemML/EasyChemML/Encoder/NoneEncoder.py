from EasyChemML.Encoder.EncoderInterface import EncoderInterface
from EasyChemML.Utilities.Application_env import Application_env
from typing import List

class NoneEncoder(EncoderInterface):

    def __init__(self, APP_ENV:Application_env):
        super().__init__(APP_ENV)

    """
    Parameter
    coulmns: defines the coulumns which are converted to RDKITMol
    nanvalue: defines the NAN value for that is used in the dataset
    """
    def convert(self, dataset, columns:List[str], n_jobs: int, **kwargs):
        pass

    @staticmethod
    def getItemname():
        return "e_NONE"

    @staticmethod
    def convert_foreach_outersplit():
        return False