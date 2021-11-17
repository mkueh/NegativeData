from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable
from EasyChemML.Utilities.DataUtilities.BatchDatatyp import BatchDatatyp, BatchDatatypClass
from EasyChemML.Utilities.DataUtilities.BatchDatatypHolder import BatchDatatypHolder
from EasyChemML.Utilities.DataUtilities.BatchTable import Batch_Access
from EasyChemML.Splitter.Splitcreator import Splitset, Split
from typing import Dict, List
import h5py, pandas, os, numpy as np, pickle, base64
import shutil, glob, zipfile
from tqdm import tqdm
from enum import Enum
import hdf5plugin

class BatchStructure:
    data_grp: h5py.Group
    tmp_grp: h5py.Group
    partition:'BatchPartition'

    def __init__(self, data_grp: h5py.Group, tmp_grp: h5py.Group, partition:'BatchPartition'):
        self.data_grp = data_grp
        self.tmp_grp = tmp_grp
        self.partition = partition

class BatchPartition(object):
    _default_chunk_size:int

    _struc:BatchStructure
    _h5Path:str
    _Databuffer:Dict[str, BatchTable]

    def __init__(self, h5_path:str, default_chunk_size=20000):
        self._h5Path = h5_path

        if os.path.exists(h5_path):
            shutil.rmtree(h5_path)

        root_grp = h5py.File(h5_path, 'a')
        tmp_grp = root_grp.create_group('tmp')
        data_grp = root_grp.create_group('data')

        self._struc = BatchStructure(data_grp, tmp_grp, self)
        self._default_chunk_size = default_chunk_size
        self._Databuffer = {}

    def __getitem__(self, item):
        return self._Databuffer[item]

    def get_struc(self):
        return self._struc

    def createDatabase(self, key, batchDtyps:BatchDatatypHolder, shape, chunksize:int=-1, data=None ,inTMP=False):
        if chunksize == -1:
            chunksize = self._default_chunk_size

        #check where
        if not inTMP:
            grp = self._struc.data_grp
            if key in grp:
                raise Exception('tablename is already exist')

        else:
            grp = self._struc.tmp_grp

            if key in grp:
                raise Exception('tablename is already exist')

        if isinstance(shape, tuple):
            size = shape[0]
        else:
            size = shape

        #check size and chunksize settings
        if size <= chunksize:
            chunksize = size

        dtypes = batchDtyps.toH5PY_dtypes()

        lz4_compressor = hdf5plugin.LZ4(nbytes=0)

        if data is None:
            if isinstance(shape,tuple) and len(shape) > 1:
                grp.create_dataset(key, dtype=dtypes, shape=shape, chunks=(chunksize,shape[1]), **lz4_compressor)
            else:
                grp.create_dataset(key, dtype=dtypes, shape=(size,), chunks=(chunksize,), **lz4_compressor)
        else:
            if isinstance(shape, tuple):
                grp.create_dataset(key, data=data, dtype=dtypes, shape=shape, chunks=(chunksize,shape[1]), **lz4_compressor)
            else:
                grp.create_dataset(key, data=data, dtype=dtypes, shape=(size,), chunks=(chunksize,), **lz4_compressor)

        grp[key].attrs['dtyps'] = base64.b64encode(pickle.dumps(obj=batchDtyps))

        if not inTMP:
            self._Databuffer[key] = BatchTable(key, chunksize, self._struc)
            return self._Databuffer[key]

        return grp[key]

    def add_PandaDataFrame(self, PD: pandas.DataFrame, asKey:str) -> BatchTable:
        # TODO Batchread in for very very lage input Data
        # TODO Multifile readin (for zinc15)
        batchDtyps:BatchDatatypHolder = BatchDatatypHolder()

        for key in PD.keys():
            col_typ = PD[key].dtype
            col_len = len(PD[key])
            chunksize = self._default_chunk_size

            if str(col_typ) == 'object':
                batchDtyps << (key, BatchDatatyp(BatchDatatypClass.NUMPY_STRING))
            else:
                batchDtyps << (key, BatchDatatyp.Fabricator_BY_str(str(col_typ)))

            if self._default_chunk_size > col_len:
                chunksize = col_len+1

        dtypes = batchDtyps.toNUMPY_dtypes()
        out = np.empty(shape=col_len, dtype=dtypes)

        for key in PD.keys():
            out[key] = PD[key].values

        self.createDatabase(asKey, batchDtyps, col_len, chunksize, out, False)

    def createSubset_reorder(self, old_table:BatchTable, split:Split, new_tableName) -> (BatchTable, Split):
        batchDtyps:BatchDatatypHolder = old_table.getDatatypes()
        chunksize = old_table.getChunksize()

        self.createDatabase(new_tableName, batchDtyps, len(old_table), chunksize)

        new_table:BatchTable = self[new_tableName]
        start_train = 0
        end_train = len(split.train)
        start_test = len(split.train)
        end_test = len(split.train) + len(split.test)

        iterator: Batch_Access = iter(new_table)
        batch: np.ndarray

        count_train = len(split.train)
        current_pos_in_train = 0
        count_test = len(split.test)
        current_pos_in_test = 0

        with tqdm(total=len(iterator), desc='create a reordered table: ') as pbar:
            for i,batch in enumerate(iterator):
                if count_train > 0:
                    if len(batch) > count_train:
                        batch[0:count_train] = old_table.get_notConverted(split.train[current_pos_in_train: current_pos_in_train+count_train])

                        #fill batch with test_items
                        check_value = len(batch)-count_train
                        batch[count_train:len(batch)] = old_table.get_notConverted(split.test[0:len(batch)-count_train])
                        current_pos_in_test += len(batch)-count_train

                        count_test -= len(batch)-count_train
                        count_train = 0
                    else:
                        batch = old_table.get_notConverted(split.train[current_pos_in_train: current_pos_in_train+len(batch)])
                        count_train -= len(batch)
                        current_pos_in_train += len(batch)
                else:
                    if len(batch) > count_test:
                        batch[0:count_test] = old_table.get_notConverted(split.test[current_pos_in_test: current_pos_in_test+count_test])
                        count_test = 0
                    else:
                        batch = old_table.get_notConverted(split.test[current_pos_in_test: current_pos_in_test+len(batch)])
                        count_test -= len(batch)
                        current_pos_in_test += len(batch)

                iterator << batch
                pbar.update(1)

        return self[new_tableName], Split(train=np.arange(start=start_train, stop=end_train), test=np.arange(start=start_test, stop=end_test))

    def cloneBatchTable(self, src_key, new_key):
        if not new_key in self._Databuffer:
            self._struc.data_grp.copy(src_key, new_key, name=new_key)
            self._Databuffer[new_key] = BatchTable(new_key, self._Databuffer[src_key].getChunksize(), self._struc)
        else:
            raise Exception('A batchtable with this key is already in the database')

    def keys(self):
        return self._Databuffer.keys()

    def get_BatchTable(self, key:str) -> BatchTable:
        return self._Databuffer[key]

    def __delitem__(self, key):
        del self._struc.data_grp[key]
        del self._Databuffer[key]

    def get_SoftlinkedList(self, key:str):
        raise Exception('Not implemented yet')

