from typing import TYPE_CHECKING
from EasyChemML.ModulSystem.ModulManager import ModulManager
from EasyChemML.Utilities.MetricUtilities.MetricFabricator import MetricFabricator
from EasyChemML.Configuration.AppSettings import AppSettings

if TYPE_CHECKING:
    from EasyChemML.Utilities.DataUtilities.BatchPartition import BatchPartition




class Application_env():

    _Modul_Manger:ModulManager

    _Output_MetricFabricator:MetricFabricator
    _Hyperparamter_MetricFabricator:MetricFabricator

    _App_Settings:AppSettings

    _TMP_PATH:str
    _WORKING_PATH:str

    def __init__(self, Modul_Manager:ModulManager, Output_MetricFabricator:MetricFabricator,
                 Hyperparamter_MetricFabricator:MetricFabricator, App_Settings:AppSettings, TMP_PATH=None, WORKING_PATH:str=''):
        self._Modul_Manger = Modul_Manager
        self._Output_MetricFabricator = Output_MetricFabricator
        self._Hyperparamter_MetricFabricator = Hyperparamter_MetricFabricator
        self._App_Settings = App_Settings
        self._TMP_PATH = TMP_PATH
        self._WORKING_PATH = WORKING_PATH

    def get_ModulManager(self):
        return self._Modul_Manger

    def get_Output_MetricFabricator(self):
        return self._Output_MetricFabricator

    def get_Hyperparameter_MetricFabricator(self):
        return self._Hyperparamter_MetricFabricator

    def get_AppSettings(self):
        return self._App_Settings

    def get_WORKING_PATH(self):
        return self._WORKING_PATH

    def get_TMP_Folder(self):
        return self._TMP_PATH

    def set_TMP_Folder(self, path:str):
        self._TMP_PATH = path




