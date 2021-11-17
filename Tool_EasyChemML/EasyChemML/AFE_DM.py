import datetime, os, logging, pandas

from typing import List, Dict

from EasyChemML.Utilities.DataUtilities.DataImporter import DataImporter
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable
from EasyChemML.Utilities.DataUtilities.BatchPartition import BatchPartition
from EasyChemML.Utilities.Dataset import Dataset, Additionaldata_Payload
from EasyChemML.Utilities.DatasetHolder import DatasetHolder
from EasyChemML.Utilities.Application_env import Application_env

from EasyChemML.HyperparameterSearch.Utilities.Config import Config
from EasyChemML.HyperparameterSearch.Config_Creator import Config_Creator
from EasyChemML.HyperparameterSearch.Algorithm.Abstract_Hyperparametersearch import Abstract_Hyperparametersearch

from EasyChemML.Runner.Modul.Abstract_Runner import Abstract_Runner

from EasyChemML.Splitter.Splitcreator import Splitcreator
from EasyChemML.Preprocessing.Preprocessing import Preprocessing
from EasyChemML.Configuration.AppSettings import AppSettings

from EasyChemML.Runner.Utilities.Job import ModelcalculationJob


class AFE_DM(object):
    Settings: AppSettings
    path_temp = None

    APP_ENV: Application_env

    def __init__(self, app_env: Application_env):
        # Fix CPU affinity
        if not os.name == 'nt': #not possible for windows
            affinity_mask = range(os.cpu_count())
            os.sched_setaffinity(os.getpid(), affinity_mask)

        self.APP_ENV = app_env

        self.path_Output = os.path.join(self.APP_ENV.get_AppSettings().workingPath, "Output")
        print('Programm wird geladen')


    def _load_inputData(self):
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! loading data !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        DI = DataImporter()
        logging.info('!!!!!!!!!!!!!! loading data !!!!!!!!!!!!!!')

        TMP_PATH = self.APP_ENV.get_TMP_Folder()
        WORKING_PATH = self.APP_ENV.get_WORKING_PATH()

        batch_partition = BatchPartition(os.path.join(TMP_PATH, 'memoryDisk.h5'), self.APP_ENV.get_AppSettings().System_chunksize)
        #self.APP_ENV.set_DataHolder(batch_partition)

        # Load data
        print('loading data from input')

        Settings = self.APP_ENV.get_AppSettings()

        print('loading feature that are not pass to the encoder')
        path_Feature = os.path.join(WORKING_PATH, Settings.Input_featurePath)
        DI.load_into_DictionaryBuffer(path_Feature, batch_partition, 'X', Type=Settings.Input_featureType,
                                      columns=Settings.Input_featureColume, **Settings.Input_featureImportSettings)

        print('loading targets')
        path_Target = os.path.join(WORKING_PATH, Settings.Input_targetPath)
        DI.load_into_DictionaryBuffer(path_Target, batch_partition, 'y', Type=Settings.Input_targetType,
                                      columns=Settings.Input_targetColume, **Settings.Input_targetImportSettings)

        additionaldata_payload = []
        if len(Settings.Additional_Datapayload) > 0:
            print('loading additional datapayload')
            for key in Settings.Additional_Datapayload:
                print(f'load payload {key}')
                name = key
                settings = Settings.Additional_Datapayload[key]

                path_Feature = os.path.join(WORKING_PATH, settings['datafile'])
                DI.load_into_DictionaryBuffer(path_Feature, batch_partition, f'X_PAYLOAD_{name}', Type=settings['inputtype'],
                                              columns=settings['feature_columne'], **settings['feature_settings'])

                path_Target = os.path.join(WORKING_PATH, Settings.Input_targetPath)
                DI.load_into_DictionaryBuffer(path_Feature, batch_partition, f'y_PAYLOAD_{name}', Type=settings['inputtype'],
                                              columns=settings['target_columne'], **settings['target_settings'])

                adp:Additionaldata_Payload = Additionaldata_Payload(name, f'X_PAYLOAD_{name}', settings['feature_encoded'], f'y_PAYLOAD_{name}', None)
                additionaldata_payload.append(adp)

        print('loading data from input is ready')

        logging.info('!!!!!!!!!!!!!! create splitting !!!!!!!!!!!!!!')
        print('!!!!!!!!!!!!!! create splitting !!!!!!!!!!!!!!')

        SC = Splitcreator(self.APP_ENV)

        splits = SC.generate_splitt(batch_partition['X'], self.APP_ENV.get_AppSettings().Input_featureColume)

        logging.info('!!!!!!!!!!!!!! splitting finished !!!!!!!!!!!!!!')
        print('!!!!!!!!!!!!!! splitting finished !!!!!!!!!!!!!!')

        dataset = Dataset('X', 'y', splits, 'InputDataset', self.path_Output,
                          TMP_PATH, self.APP_ENV.get_AppSettings().Input_featureColumeEncoding, batch_partition, additionaldata_payload)

        datasetHolder = DatasetHolder()
        datasetHolder << dataset

        return datasetHolder

    def start(self):
        TMP_PATH = os.path.join(self.APP_ENV.get_AppSettings().workingPath, 'TMP')
        self.APP_ENV.set_TMP_Folder(TMP_PATH)

        if not os.path.exists(TMP_PATH):
            print('TMP_PATH not found ... i create the folder for you')
            os.mkdir(TMP_PATH)

        datasetHolder = self._load_inputData()


        logging.info('!!!!!!!!!!!!!! Encoding+Preprocessing !!!!!!!!!!!!!!')
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Encoding+Preprocessing !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        PP = Preprocessing(self.APP_ENV)
        CC = Config_Creator(self.APP_ENV)

        # Convert feature with the selected encoder
        encoder = self.APP_ENV.get_ModulManager().get_encoder(self.APP_ENV.get_AppSettings().Encoder)(self.APP_ENV)
        self.__generateDatastep_encoder(datasetHolder, self.APP_ENV.get_AppSettings().workingPath, 'encoding', encoder,
                                **self.APP_ENV.get_AppSettings().Encoder_settings)

        # Preprocessing
        self.__generateDatastep_prepro(datasetHolder, self.APP_ENV.get_AppSettings().workingPath, 'preprocessing', PP, **dict())

        logging.info('!!!!!!!!!!!!!! Encoding+Preprocessing  finished!!!!!!!!!!!!!!')

        #flatten
        print('flatt Features')
        for dataset in datasetHolder:
            dataset.getFeature_data().flattBatchTable()
        print('flatt Targets')
        for dataset in datasetHolder:
            dataset.getTargets_data().flattBatchTable()

        logging.info('!!!!!!!!!!!!!! OuterCV-Configuration creation !!!!!!!!!!!!!!')
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! Config creation !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        model_name = self.APP_ENV.get_AppSettings().Model_algo
        model_args = self.APP_ENV.get_AppSettings().Model_algoSettings

        output_folder = os.path.join(self.APP_ENV.get_AppSettings().workingPath, 'Output')
        configs = CC.createConfigurations(datasetHolder, model_name, model_args)

        runner = self.APP_ENV.get_ModulManager().get_runner(self.APP_ENV.get_AppSettings().Jobrunner)

        # init
        runner = runner(output_folder, self.APP_ENV.get_AppSettings().Jobrunner_settings, self.APP_ENV)

        hypersearch = self.APP_ENV.get_ModulManager().get_hyperSearch(
            self.APP_ENV.get_AppSettings().HyperparamterSearch)
        # init
        hypersearch = hypersearch(self.APP_ENV.get_AppSettings().Hyperparamter_metric,
                                  os.path.join(output_folder, 'HyperparameterSearch'), self.APP_ENV,
                                  self.APP_ENV.get_AppSettings().HyperparamterSearch_settings)

        self._run_learning(configs, hypersearch, runner)

        print("finished")

    """
    generate preprocessing of encoding
    If the preprocessing exists, it will be loaded from the existing file.
    
    PP.convertData(dataset)
    """

    def __generateDatastep_encoder(self, datasetHolder: DatasetHolder, workingdir: str, info_filename: str, encoder_class,
                           **convertMethod_settings):
        if encoder_class.convert_foreach_outersplit():
            if datasetHolder.splitted and not len(datasetHolder) == 1:
                raise Exception('datasetHolder contains more dataset than possible at this position')
            else:
                datasetHolder.split_and_copy()

                for dataset in datasetHolder:
                    encoder_class.convert(dataset, dataset.getEncoding_Columns(), -1, **convertMethod_settings)
        else:
            dataset = datasetHolder[0]
            encoder_class.convert(dataset, dataset.getEncoding_Columns(), -1, **convertMethod_settings)

    def __generateDatastep_prepro(self, datasetHolder: DatasetHolder, workingdir: str, info_filename: str, convertMethod,
                           **convertMethod_settings):

        for dataset in datasetHolder:
            convertMethod.convert(dataset, dataset.getEncoding_Columns(), -1, **convertMethod_settings)


    def _HypersearchNeeded(self, configs: List[Config]):
        configs_withHP = []
        for c in configs:
            if c.containHyperparameter:
                configs_withHP.append(c)
        return configs_withHP

    def _run_learning(self, configs: List[Config], hypersearch=None, runner=None):
        logging.info('Learning is started')
        logging.info('Time: ' + str(datetime.datetime.now()))

        configs_withHP = self._HypersearchNeeded(configs)

        if len(configs_withHP) == len(configs):
            logging.info('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            logging.info(f'Nested-CV because there are {len(configs)} hyperparamters')
            logging.info('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            best_settings = self._run_hyperparameterSearch(configs, runner, hypersearch)
            self._run_outerLearning(best_settings, configs, runner)
        elif len(configs_withHP) == 0:
            logging.info('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            logging.info('NO Nested-CV because there are no different hyperparamters')
            logging.info('%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%')
            best_settings = {}

            for c in configs:
                best_settings[c] = {'best_param': c.implicit_algorithm_para}

            self._run_outerLearning(best_settings, configs, runner)
        else:
            raise Exception('There are external splits without hyperparameter and some with. This is not supported')

    def _run_hyperparameterSearch(self, configs: List[Config], runner: Abstract_Runner,
                                  hyperParamterSearch: Abstract_Hyperparametersearch):
        best_settings = hyperParamterSearch.performe_HyperparamterSearch(configs, runner)
        self._CSV_hyperparameterMetrics(bestsettings=best_settings,
                                        path=os.path.join(self.APP_ENV.get_AppSettings().workingPath, 'Output'),
                                        CSV_filename='Hyperparametersearch_results.csv')
        return best_settings  # TODO add best parameter to CSV

    def _CSV_hyperparameterMetrics(self, bestsettings: Dict[Config, Dict], path: str, CSV_filename: str):
        out_array = []

        # Header
        line_arr = ['Outer CV Step', 'best_param']
        metric = bestsettings[list(bestsettings.keys())[0]]['metric']

        for key in metric:
            line_arr.append(key)

        out_array.append(line_arr)

        for i, c in enumerate(bestsettings):
            line_arr = []
            line_arr.append(f'OuterCV {c.config_id}')
            para = bestsettings[c]['best_param']
            line_arr.append(f'{para}')
            metric = bestsettings[c]['metric']

            for key in metric:
                line_arr.append(metric[key])

            out_array.append(line_arr)

        dataFrame_results = pandas.DataFrame(out_array)
        dataFrame_results.to_csv(os.path.join(path, CSV_filename), header=False, index=False)

    def _run_outerLearning(self, bestpara: Dict[Config, Dict], configs: List[Config],
                           runner: Abstract_Runner):
        model_jobs = []
        for i, c in enumerate(configs):
            self._replaceParamWithFixed(bestpara[c]['best_param'], self.APP_ENV.get_AppSettings().Fixparam_forOuter)
            model_job = ModelcalculationJob(f'ModelJob_Config:{i}', c.algorithm, bestpara[c]['best_param'], c)
            model_jobs.append(model_job)
        runner.run_Jobs(model_jobs)

    def _replaceParamWithFixed(self, best_para: Dict, fixed_para: Dict):
        for key in best_para:
            if key in fixed_para:
                best_para[key] = fixed_para[key]
        return best_para
