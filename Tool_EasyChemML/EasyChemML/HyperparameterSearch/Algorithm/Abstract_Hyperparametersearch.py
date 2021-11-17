from EasyChemML.Utilities.Application_env import Application_env

class Abstract_Hyperparametersearch():
    APP_ENV:Application_env

    def __init__(self, APP_ENV:Application_env):
        self.APP_ENV = APP_ENV

    @staticmethod
    def getItemname():
        return "abstractHyperparametersearch"

    def isparalle(self): #TODO implememnt
        return False