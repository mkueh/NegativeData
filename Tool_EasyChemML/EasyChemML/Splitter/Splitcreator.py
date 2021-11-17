from EasyChemML.Configuration.AppSettings import AppSettings
from EasyChemML.Utilities.Application_env import Application_env
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable

from EasyChemML.Utilities.CompressUtilities.lz4_compressor import lz4_compressor

from typing import List, Dict
import numpy as np, os, lz4.frame, pickle

class Splitsettings(object):
    param:Dict
    algo:str

    def __init__(self, param:Dict, algo:str):
        self.param = param
        self.algo = algo

class Split(object):
    train = None
    test = None

    def __init__(self, train:List, test:List):
        self.train = train
        self.test = test
        if not self.checkIfIncreasedOrder():
            print('The indicies of a split must be specified in ascending order.')
            print('sorting...')
            self.test = np.sort(self.test)
            self.train = np.sort(self.train)


    def checkIfIncreasedOrder(self):
        return np.all(np.diff(self.train) > 0) and np.all(np.diff(self.test) > 0)

class Splitset(object):
    _out_splits:List[Split] = None
    _in_splits:List[Split] = None

    _out_splits_settings:Splitsettings = None
    _in_splits_settings:Splitsettings = None

    def __init__(self, out_split:List[Split], in_splits:List[Split], out_split_settings:Splitsettings=None, in_split_settings:Splitsettings=None):
        self._out_splits = out_split
        self._in_splits = in_splits

        self._out_splits_settings = out_split_settings
        self._in_splits_settings = in_split_settings

    def get_outer_split(self, index_outer):
        return self._out_splits[index_outer]

    def get_outer_splitts(self):
        return self._out_splits

    def get_inner_split(self, index_outer, index_inner):
        return self._in_splits[index_outer][index_inner]

    def get_inner_splitts(self, index_outer):
        return self._in_splits[index_outer]

    def get_out_splits_settings(self):
        return self._out_splits_settings

    def get_in_splits_settings(self):
        return self._in_splits_settings

    """
    Since the inner distribution is calculated and stored relative to the outer one, this function helps to calculate absolute indices for the nested cv
    """
    def get_inner_split_absolut(self, index_outer, index_inner):
        train = [self._out_splits[index_outer].train[i] for i in self._in_splits[index_outer][index_inner].train]
        test = [self._out_splits[index_outer].train[i] for i in self._in_splits[index_outer][index_inner].test]
        return Split(train, test)

    def get_outerCount(self):
        return len(self._out_splits)

    def get_innerCount(self, outer_index):
        return len(self._in_splits[outer_index])


class Splitcreator(object):
    APP_ENV:Application_env

    def __init__(self, app_env: Application_env):
        self.APP_ENV = app_env

    """Generate the splitting indices"""
    def generate_splitt(self, train_raw:BatchTable, column, feature_subset=None) -> Split:
        settings = self.APP_ENV.get_AppSettings()

        if not settings.Splitter_saveLoadSplit == '' and os.path.exists(settings.Splitter_saveLoadSplit):
            print(f'Split is loaded from the file: {settings.Splitter_saveLoadSplit}')
            load_split = self._load_split(settings.Splitter_saveLoadSplit)
            return load_split

        args_in = settings.Splitter_innerSettings
        args_out = settings.Splitter_outerSettings

        # for Scikitlearn_Splitter
        args_in['splitter'] = settings.Splitter_innerSplitter
        args_in['raw_column'] = column
        args_out['splitter'] = settings.Splitter_outerSplitter
        args_out['raw_column'] = column

        # get Splitter from ModuleManager
        inner_splitter = self.APP_ENV.get_ModulManager().get_splitter(settings.Splitter_innerSplitter)()
        outer_splitter = self.APP_ENV.get_ModulManager().get_splitter(settings.Splitter_outerSplitter)()

        out_splits = self._warp2Split(outer_splitter.split(train_raw, **args_out))
        in_splits = []

        for i, _ in enumerate(out_splits):
            if feature_subset is None:
                in_splits.append(self._warp2Split(inner_splitter.split(self._getarrindices(train_raw, out_splits[i].train),
                                                          **args_in)))
        out = Splitset(out_splits, in_splits, args_out, args_in)

        if not settings.Splitter_saveLoadSplit == '':
            self._save_split(out, settings.Splitter_saveLoadSplit)

        return out

    def _warp2Split(self, splits:List[List]):
        tmp = []

        for split in splits:
            tmp.append(Split(split[0], split[1]))

        return tmp

    def _getarrindices(self, arr, indicies):
        return arr.createShadowTable(indicies=indicies)

    def _save_split(self, split:Splitset, path:str):
        lz4 = lz4_compressor()
        lz4.compress_object_to_file(split, path)

    def _load_split(self, path:str):
        lz4 = lz4_compressor()
        return lz4.decompress_object_from_file(path)
