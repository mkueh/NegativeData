import os, sys, glob, importlib, importlib.util
from typing import Dict
import EasyChemML.ConfigGenerator
import inspect


class ModulManager(object):
    __encoder_DB = {}
    __splitter_DB = {}
    __model_DB = {}
    __prepro_DB = {}
    __runner_DB = {}
    __hyper_DB = {}


    def __autoload_dir(self, path: str, package: str, dict: Dict):

        pyDataToload = glob.glob(os.path.join(path, '*.py'))
        
        for py in pyDataToload:
        
            if py[-11:] == '__init__.py':
              continue
        
            try:
                plugin_spec = importlib.util.spec_from_file_location(os.path.basename(py), py)
                plugin = importlib.import_module(package + str(plugin_spec.parent))
                item_class = getattr(plugin, str(plugin_spec.parent))
                dict[item_class.getItemname()] = item_class
            except Exception as E:
                print('Can not import ' + package.split('.')[0] + ': ' + str(py))
                print(E)

    def __init__(self, root_path_override:str = None):

        super()
        if root_path_override is None:
            self_path = os.path.dirname(inspect.getfile(self.__class__))
            root_path = os.path.dirname(self_path)

            encoder_path = os.path.join(root_path, 'Encoder')
            splitter_path = os.path.join(root_path, 'Splitter', 'Modul')
            model_path = os.path.join(root_path, 'Model')
            prepro_path = os.path.join(root_path, 'Preprocessing', 'Modul')
            hyper_path = os.path.join(root_path, 'HyperparameterSearch', 'Algorithm')
            runner_path = os.path.join(root_path, 'Runner', 'Modul')
        else:
            encoder_path = os.path.join(root_path_override, 'Encoder')
            splitter_path = os.path.join(root_path_override, 'Splitter', 'Modul')
            model_path = os.path.join(root_path_override, 'Model')
            prepro_path = os.path.join(root_path_override, 'Preprocessing', 'Modul')
            hyper_path = os.path.join(root_path_override, 'HyperparameterSearch', 'Algorithm')
            runner_path = os.path.join(root_path_override, 'Runner', 'Modul')

        self.__autoload_dir(encoder_path, 'EasyChemML.Encoder.', self.__encoder_DB)
        self.__autoload_dir(splitter_path, 'EasyChemML.Splitter.Modul.', self.__splitter_DB)
        self.__autoload_dir(model_path, 'EasyChemML.Model.', self.__model_DB)
        self.__autoload_dir(prepro_path, 'EasyChemML.Preprocessing.Modul.', self.__prepro_DB)
        self.__autoload_dir(hyper_path, 'EasyChemML.HyperparameterSearch.Algorithm.', self.__hyper_DB)
        self.__autoload_dir(runner_path, 'EasyChemML.Runner.Modul.', self.__runner_DB)
        pass

    """
    return the encoder class
    """

    def get_encoder(self, name):
        if name in self.__encoder_DB:
            return self.__encoder_DB[name]
        else:
            raise Exception(f'Encoder name ({name}) is wrong or could not be loaded')

    """
    return the splitter class
    """

    def get_splitter(self, name):
        if 'scikit_splitter' in self.__splitter_DB:
            check = self.__splitter_DB['scikit_splitter'].regSplitter()
            if name in check:
                return self.__splitter_DB['scikit_splitter']
        if name in self.__splitter_DB:
            return self.__splitter_DB[name]
        else:
            raise Exception(f'Splitter name ({name}) is wrong or could not be loaded')

    """
    return the model class
    """

    def get_model(self, name):
        if name in self.__model_DB:
            return self.__model_DB[name]
        else:
            raise Exception(f'Model name ({name}) is wrong or could not be loaded')

    """
    :return preprocessing class
    """

    def get_prepro(self, name):
        if name in self.__prepro_DB:
            return self.__prepro_DB[name]
        else:
            raise Exception(f'Preprocessing name ({name}) is wrong or could not be loaded')

    """
    :return hyperparameter-search class
    """

    def get_hyperSearch(self, name):
        if name in self.__hyper_DB:
            return self.__hyper_DB[name]
        else:
            raise Exception(f'Hyperparameter-search name ({name}) is wrong or could not be loaded')

    """
    :return runner class
    """

    def get_runner(self, name):
        if name in self.__runner_DB:
            return self.__runner_DB[name]
        else:
            raise Exception(f'Runner name ({name}) is wrong or could not be loaded')


#from Model.Abstract_Model import Abstract_Model
#from Encoder.EncoderInterface import EncoderInterface
#from Runner.Modul.Abstract_Runner import Abstract_Runner
#from HyperparameterSearch.Algorithm.Abstract_Hyperparametersearch import Abstract_Hyperparametersearch