from .EncoderInterface import EncoderInterface
from .__FingerprintEncoder.FingerprintGenerator import FingerprintGenerator
from .MolRdkitConverter import MolRdkitConverter
from EasyChemML.Utilities.Application_env import Application_env
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable, Batch_Access
from EasyChemML.Utilities.DataUtilities.BatchDatatyp import BatchDatatyp, BatchDatatypClass
from EasyChemML.Utilities.DataUtilities.BatchDatatypHolder import BatchDatatypHolder
from EasyChemML.Utilities.Dataset import Dataset

import math, numpy as np
from typing import List, Dict

from EasyChemML.Utilities.ParallelUtilities.IndexQueues.IndexQueue_settings import IndexQueue_settings
from EasyChemML.Utilities.ParallelUtilities.ParallelHelper import ParallelHelper
from EasyChemML.Utilities.ParallelUtilities.Shared_PythonList import Shared_PythonList


class FingerprintEncoder(EncoderInterface):

    def __init__(self, APP_ENV:Application_env):
        super().__init__(APP_ENV)

    """
    Input is raw SMILES!
    Output is the __FingerprintEncoder dict

    Parameter
    FP_length:
    coulmns: if None than all
    """

    def convert(self, dataset:Dataset, columns:List[str], n_jobs: int, **kwargs):
        if not 'fp_names' in kwargs:
            print('__FingerprintEncoder: fp_names is not set')
        if not 'fp_settings' in kwargs:
            print('__FingerprintEncoder: fp_settings is not set')

        MolRdkitConverter(self.APP_ENV).convert(dataset=dataset, columns=columns ,n_jobs=n_jobs, kwargs=kwargs)
        self._convertData(dataset.getFeature_data(), columns, n_jobs, kwargs['fp_names'], kwargs['fp_settings'])

    def _convertData(self, InputBuffer: BatchTable, columns:List[str], n_jobs:int, fp_names:List, fp_settings:Dict):
        FG = FingerprintGenerator()
        emptyOne = FG.generateArrofFingerprints(['NA']*len(columns), fp_names, fp_settings)

        size = 0
        for col in emptyOne:
            size += len(col)

        iterator:Batch_Access = iter(InputBuffer)
        batch: np.ndarray
        dataTypHolder: BatchDatatypHolder = InputBuffer.getDatatypes()

        for column in columns:
            dataTypHolder[column] = BatchDatatyp(BatchDatatypClass.NUMPY_INT8, (int(size/len(columns)),))

        for batch in iterator:
            out = dataTypHolder.createAEmptyNumpyArray(len(batch))
            shared_batch = Shared_PythonList(batch, InputBuffer.getDatatypes())
            parallel_executer = ParallelHelper(n_jobs)
            IQ_settings = IndexQueue_settings(start_index=0, end_index=len(batch), chunksize=128)
            out = parallel_executer.execute_map_orderd_return(self._parallel_convert, IQ_settings, out.dtype,
                                                              input_arr = shared_batch, columns = columns, fp_names=fp_names,
                                                              fp_settings=fp_settings)

            iterator <<= out

    def _parallel_convert(self,input_arr: Shared_PythonList, columns: List[str], out_dtypes, current_chunk:int, fp_names, fp_settings):
        FG = FingerprintGenerator()
        out_array = np.empty(shape=(len(current_chunk),), dtype=out_dtypes)
        index_counter = 0

        for current_index in current_chunk:
            raise_exception = False
            try:
                col_arr = FG.generateArrofFingerprints(input_arr[current_index][columns], fp_names, fp_settings)
            except Exception as e:
                print(f'Data (row: {current_index} ,column: {exists_col}) can not translate in a RDKit mol object')
                print('Exception : ' + str(e))
                raise Exception('Data could not be converted')


            for exists_col in list(input_arr.getcolumns()):
                if exists_col not in columns:
                    out_array[index_counter][exists_col] = input_arr[current_index][exists_col]

            for i, arr in enumerate(col_arr):
                out_array[index_counter][columns[i]] = col_arr[i]

            index_counter += 1
        return out_array

    @staticmethod
    def getItemname():
        return "e_fpc"

    @staticmethod
    def isparallel():
        return True

    @staticmethod
    def convert_foreach_outersplit():
        return False
