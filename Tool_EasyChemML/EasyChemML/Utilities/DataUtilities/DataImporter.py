from enum import Enum
import os, pandas, tables, numpy as np
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable
from EasyChemML.Utilities.DataUtilities.BatchPartition import BatchPartition

from typing import List, Tuple


class Input_Type(Enum):
    CSV = 1
    XLSX = 2

class DataImporter(object):

    def _loadCSV(self, path:str, dataHolder:BatchPartition, key:str, usecols, range:Tuple[int, int]=(-1,-1)):
        if range[0] < 0 or range[1] < 0:
            panda_dataframe = pandas.read_csv(path, usecols=usecols,  index_col=False)
        else:
            panda_dataframe = pandas.read_csv(path, usecols=usecols, index_col=False)
            panda_dataframe = panda_dataframe[range[0]:range[1]]
        #panda_dataframe = self._reduce_mem_usage(panda_dataframe)
        dataHolder.add_PandaDataFrame(panda_dataframe, key)

    def _loadXLSX(self, path:str, dataHolder:BatchPartition, key:str, usecols, sheet_name, range:Tuple[int, int]=(-1,-1)):
        if range[0] < 0 or range[1] < 0:
            panda_dataframe = pandas.read_excel(path, usecols=usecols, index_col=False, sheet_name=sheet_name)
        else:
            panda_dataframe = pandas.read_excel(path, usecols=usecols, index_col=False, sheet_name=sheet_name)
            panda_dataframe = panda_dataframe[range[0]:range[1]]
        #panda_dataframe = self._reduce_mem_usage(panda_dataframe)
        dataHolder.add_PandaDataFrame(panda_dataframe, key)

    def _reduce_mem_usage(self, df):
        """
        iterate through all the columns of a dataframe and modify the data type to reduce memory usage.

        https://www.kaaggle.com/gemartin/load-data-reduce-memory-usage
        """
        start_mem = df.memory_usage().sum() / 1024 ** 2
        print('Memory usage of dataframe is {:.2f} MB'.format(start_mem))

        for col in df.columns:
            col_type = df[col].dtype

            if col_type != object:
                c_min = df[col].min()
                c_max = df[col].max()
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df[col] = df[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df[col] = df[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df[col] = df[col].astype(np.int32)
                    elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                        df[col] = df[col].astype(np.int64)
                else:
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df[col] = df[col].astype(np.float16)
                    elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                        df[col] = df[col].astype(np.float32)
                    else:
                        df[col] = df[col].astype(np.float64)
            else:
                pass

        end_mem = df.memory_usage().sum() / 1024 ** 2
        print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
        print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))
        return df

    def load_into_DictionaryBuffer(self, path:str, dataHolder:BatchPartition, key:str, Type:Input_Type, **kwargs):
        try:
            Type = Input_Type(Type)
        except:
            print('Input_Type not exist')
            raise Exception('Input_Type: '+str(Type)+' not exist')

        #if CSV-Data
        if Type == Input_Type.CSV:
            if 'range' in kwargs:
                self._loadCSV(path, dataHolder, key, usecols=kwargs['columns'], range=kwargs['range'])
            else:
                self._loadCSV(path, dataHolder, key, usecols=kwargs['columns'])

        #if XLSX
        elif Type == Input_Type.XLSX:
            if 'range' in kwargs:
                self._loadXLSX(path, dataHolder, key, usecols=kwargs['columns'], sheet_name=kwargs['sheet_name'], range=kwargs['range'])
            else:
                self._loadXLSX(path, dataHolder, key, usecols=kwargs['columns'], sheet_name=kwargs['sheet_name'])
        else:
            print('Input_Type not exist')
            raise Exception('Input_Type: '+str(Type)+' not exist')

