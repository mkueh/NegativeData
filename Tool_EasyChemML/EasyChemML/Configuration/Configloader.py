from EasyChemML.Configuration.AppSettings import AppSettings
import ast, os, hjson, logging, shutil

from typing import List, Dict

class Configloader(object):

    configfilepath = str
    configfile = None
    logger = -1
    stop_code = False

    def __init__(self, configpath:str):
        self.configfilepath = configpath
        self.configfile = self._loadHjson(configpath)

    def _loadHjson(self, path) -> dict:
        if os.path.exists(path):
            self._createLogger(os.path.dirname(path))
            with open(path, 'r', encoding='utf8') as json_file:
                data = hjson.load(json_file)
            self.logger.info('Configloader start working')
            return data
        else:
            self.logger.info('Configloader crashed  -  Configloader can not find the file')
            raise Exception('Configloader can not find the file')

    def _createLogger(self, log_dir):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        if os.path.exists('Configloader.log'):
            os.remove('Configloader.log')

        file_handler = logging.FileHandler('Configloader.log')
        formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
        file_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)

    def _loadSettingfromDict(self, section, parameter, typ=str, default=None, listdict_check=False):
        if section in self.configfile:
            if parameter is None:
                try:
                    return typ(self.configfile[section])
                except:
                    self.stop_code = True
                    self.logger.error(f'Error in Config-Loader at {section} -> {parameter}')
            if parameter in self.configfile[section]:
                try:
                    input = typ(self.configfile[section][parameter])

                    if listdict_check and input[0] == '[' and input[-1] == ']':
                        input = list(self.configfile[section][parameter])
                    elif listdict_check and input[0]  == '{' and input[-1] == '}':
                        input = dict(self.configfile[section][parameter])

                    if not input is None and isinstance(input, str):
                        input = input.strip()

                    elif input is None:
                        raise Exception(f'E1-Entry not found: {section} -> {parameter}')

                    return input
                except Exception as e:
                    self.stop_code = True
                    self.logger.error(f'Error in Config-Loader at {section} -> {parameter}')
                    self.logger.error(f'{e}')
            else:
                if default is None:
                    self.stop_code = True
                    self.logger.error('Parameter '+parameter+' missing in the settings file and there is no default value')
                else:
                    self.logger.info('Parameter ' + parameter + f' missing in the settings file. Value set to the default value: {default}')
                    return default
        else:
            self.stop_code = True
            self.logger.error('Section is '+section+' missing in the settings file')

    def getLearningsettings(self) -> AppSettings:
        temp = AppSettings()

        # input_settings
        temp.Input_featureType = int(self._loadSettingfromDict('input_settings', 'feature_inputtype', int))
        temp.Input_targetType = int(self._loadSettingfromDict('input_settings', 'target_inputtype', int))

        temp.Input_featurePath = self._loadSettingfromDict('input_settings', 'feature_path')
        temp.Input_targetPath = self._loadSettingfromDict('input_settings', 'target_path')

        temp.Input_featureColume = self._loadSettingfromDict('input_settings', 'feature_colume', list)
        temp.Input_featureColumeEncoding = self._loadSettingfromDict('input_settings', 'feature_encoded', list)
        temp.Input_targetColume = self._loadSettingfromDict('input_settings', 'target_colume', list)

        temp.Input_featureImportSettings = self._loadSettingfromDict('input_settings', 'feature_Inputsettings', dict)
        temp.Input_targetImportSettings = self._loadSettingfromDict('input_settings', 'target_Inputsettings', dict)

        temp.Additional_Datapayload = self._loadSettingfromDict('input_settings', 'additional_datapayload', dict, default={})

        # splitter_settings
        temp.Splitter_innerSplitter = self._loadSettingfromDict('splitter_settings', 'inner_splitter')
        temp.Splitter_innerSettings = self._loadSettingfromDict('splitter_settings', 'inner_splittersettings', dict)

        temp.Splitter_outerSplitter = self._loadSettingfromDict('splitter_settings', 'outer_splitter')
        temp.Splitter_outerSettings = self._loadSettingfromDict('splitter_settings', 'outer_splittersettings', dict)

        temp.Splitter_saveLoadSplit = self._loadSettingfromDict('splitter_settings', 'saveLoad_split', str, default='')

        # encoder_settings
        temp.Encoder = self._loadSettingfromDict('encoder_settings', 'encoder', default='e_NONE')
        temp.Encoder_settings = self._loadSettingfromDict('encoder_settings', 'encoder_settings', dict, default={})

        # preprocessing_settings
        temp.Preprocessing_feature_Steps = self._loadSettingfromDict('preprocessing_settings', 'Preprocessing_feature_Steps', List[str], default=[])
        temp.Preprocessing_feature_Steps_param = self._loadSettingfromDict('preprocessing_settings',
                                                                     'Preprocessing_feature_Steps_param', List[Dict],
                                                                     default=[])

        temp.Preprocessing_target_Steps = self._loadSettingfromDict('preprocessing_settings', 'Preprocessing_target_Steps', List[str], default=[])
        temp.Preprocessing_target_Steps_param = self._loadSettingfromDict('preprocessing_settings',
                                                                     'Preprocessing_target_Steps_param', List[Dict],
                                                                     default=[])

        #hyperparamterSearch_settings
        temp.HyperparamterSearch = self._loadSettingfromDict('hyperparamterSearch_settings', 'hyperparamterSearch_algo', default='grid_search')
        temp.HyperparamterSearch_settings = self._loadSettingfromDict('hyperparamterSearch_settings', 'hyperparamterSearch_param', dict, default='{}')
        temp.Fixparam_forOuter = self._loadSettingfromDict('hyperparamterSearch_settings', 'fixparam_forOuter', dict, default={})

        #jobrunner_settings
        temp.Jobrunner = self._loadSettingfromDict('jobrunner_settings', 'jobrunner', default='local_runner')
        temp.Jobrunner_settings = self._loadSettingfromDict('jobrunner_settings', 'jobrunner_para', dict, default={})

        # model_settings
        temp.Model_algo = self._loadSettingfromDict('model_settings', 'using_algo', str, default='m_NONE')
        temp.Model_algoSettings = self._loadSettingfromDict('model_settings', 'using_algosettings', dict, default={})

        # analytic_settings
        temp.Output_metrics = self._loadSettingfromDict('analytic_settings', 'output_metrics', list, default=['r2_score'])
        temp.Output_metrics_settings = self._loadSettingfromDict('analytic_settings', 'output_metrics_settings', list, default=[{}])
        temp.Output_metrics, temp.Output_metrics_settings = self._createMetric_settings(temp.Output_metrics, temp.Output_metrics_settings)

        temp.Hyperparamter_metric = self._loadSettingfromDict('analytic_settings', 'optimise_metric', str, default='r2_score')
        temp.Hyperparamter_setting = self._loadSettingfromDict('analytic_settings', 'optimise_metric_settings', dict, default={})
        temp.Hyperparamter_metric, temp.Hyperparamter_setting = self._createMetric_settings([temp.Hyperparamter_metric],
                                                                                        [temp.Hyperparamter_setting])

        temp.System_chunksize = self._loadSettingfromDict('system_settings', 'batch_chunksize', int, 100000)

        temp = self._checkSettings(temp)

        if self.stop_code:
            raise Exception('settings data contains errors... for more informations look in the Configloader.log file')

        return temp


    """
    This function is intended to check the consistency of the settings.hjson file. If new modules are added/used the
    settings.hjson file will be extended automatically and the program will exit with an error.
    Currently this function is not supported
    """
    def _checkSettings(self, settings:AppSettings) -> bool:
        if isinstance(settings.Model_algo, list) and isinstance(settings.Model_algoSettings, list):
            if not len(settings.Model_algo) == len(settings.Model_algoSettings):
                raise Exception('!len of using_algo and using_algosettings is different!')

        return settings

    """
    Metric reconstruction
    """
    def _createMetric_settings(self, names:List, settings:List[Dict]):
        if len(settings) == 1 and len(settings[0]) == 0:
            output_settings = []
            for i in range(len(names)):
                output_settings.append({})
            return names, output_settings

        output_settings = []
        set:str
        for set in settings:
            if '_' in set:
                _count = set.count('_')
                for i in range(_count):
                    output_settings.append({})
            elif isinstance(set, dict):
                output_settings.append(set)
            else:
                self.stop_code = True
                self.logger.error('wrong paramter in metric_settings')
        if len(names) == len(output_settings):
            return names, output_settings
        else:
            self.stop_code = True
            self.logger.error('wrong paramter in metric_settings')



