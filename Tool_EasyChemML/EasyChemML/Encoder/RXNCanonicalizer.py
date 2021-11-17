from EasyChemML.Encoder.EncoderInterface import EncoderInterface
from EasyChemML.Utilities.Dataset import Dataset
from typing import List
from EasyChemML.Utilities.Application_env import Application_env
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable, Batch_Access
from EasyChemML.Utilities.DataUtilities.BatchDatatyp import BatchDatatypClass
from EasyChemML.Utilities.DataUtilities.BatchDatatypHolder import BatchDatatypHolder
from EasyChemML.Utilities.ParallelUtilities.ParallelHelper import ParallelHelper
from EasyChemML.Utilities.ParallelUtilities.IndexQueues.IndexQueue_settings import IndexQueue_settings
from EasyChemML.Utilities.ParallelUtilities.Shared_PythonList import Shared_PythonList
import math, numpy as np, pickle
from rxnfp.tokenization import (process_reaction)
import pkg_resources


class RXNCanonicalizer(EncoderInterface):

    def __init__(self, APP_ENV:Application_env):
        super().__init__(APP_ENV)

    """
    Parameter
    coulmns: defines the coulumns which are canonicalized (only one column can be handled)
    nanvalue: defines the NAN value for that is used in the dataset
    """
    def convert(self, dataset:Dataset, columns:List[str], n_jobs:int, **kwargs):
        self.__canonicalizeRXNSMILES(InputBuffer=dataset.getFeature_data(), columns=columns, n_jobs=n_jobs)


    def __canonicalizeRXNSMILES(self, InputBuffer:BatchTable, columns:List[str], n_jobs: int):
        iterator: Batch_Access = iter(InputBuffer)
        batch: np.ndarray
        dataTypHolder: BatchDatatypHolder = InputBuffer.getDatatypes()

        if len(columns) > 1:
            raise Exception('Only one rxnSMILES can be handeled.')

        for column in columns:
            dataTypHolder[column] = BatchDatatypClass.PYTHON_OBJECT

        for batch in iterator:
            shared_batch = Shared_PythonList(batch, InputBuffer.getDatatypes())
            out = dataTypHolder.createAEmptyNumpyArray(len(batch))
            parallel_executer = ParallelHelper(n_jobs)
            IQ_settings = IndexQueue_settings(start_index=0, end_index=len(batch), chunksize=128)
            out = parallel_executer.execute_map_orderd_return(self._parallel_convert,IQ_settings,out.dtype,
                                                               columns=columns, input_arr = shared_batch)
            iterator <<= out
            shared_batch.destroy()


    def _parallel_convert(self, input_arr: Shared_PythonList, columns: List[str], out_dtypes, current_chunk:int):
        out_array = np.empty(shape=(len(current_chunk),), dtype=out_dtypes)
        index_counter = 0
        for current_index in current_chunk:
            for exists_col in list(input_arr.getcolumns()):
                if exists_col in columns:
                    if isinstance(input_arr[current_index][exists_col], float):
                        if math.isnan(input_arr[current_index][exists_col]):
                            out_array[current_index][exists_col] = 'NA'
                            pass
                    elif input_arr[current_index][exists_col] == 'nan' or input_arr[current_index][exists_col] == 'NA':
                        out_array[current_index][exists_col] = 'NA'
                        pass
                    else:
                        canonical_rxn = None
                        try:
                            canonical_rxn = process_reaction(input_arr[current_index][exists_col].decode("utf-8"))

                        except Exception as e:
                            print(e)

                        if canonical_rxn is None:
                            print("cant convert " + str(input_arr[current_index][exists_col]))
                            print(f'set {current_index} {exists_col} to NA')
                            out_array[index_counter][exists_col] = 'NA'
                        else:
                            out_array[index_counter][exists_col] = canonical_rxn
                else:
                    out_array[index_counter][exists_col] = input_arr[current_index][exists_col]
            index_counter += 1
        return out_array

    @staticmethod
    def getItemname():
        return "e_rxn_canonical"

    @staticmethod
    def isparallel():
        return False

    @staticmethod
    def convert_foreach_outersplit():
        return False