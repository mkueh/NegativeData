import h5py, math, numpy as np, pickle, base64, codecs
from EasyChemML.Utilities.Performance.Performance_analysis import benchmark_function
from EasyChemML.Utilities.DataUtilities.BatchDatatyp import BatchDatatyp, BatchDatatypClass
from EasyChemML.Utilities.DataUtilities.BatchDatatypHolder import BatchDatatypHolder
from typing import List, TYPE_CHECKING, Tuple
from collections.abc import Iterable

if TYPE_CHECKING:
    from .BatchPartition import BatchPartition, BatchStructure
    from EasyChemML.Splitter.Splitcreator import Split


class BatchTable:
    _h5_dataset_key: str
    _chunksize: int
    _Bstruct: 'BatchStructure'

    def __init__(self, h5_dataset_key: str, chunksize: int, Bstruct: 'BatchStructure'):
        self._h5_dataset_key = h5_dataset_key
        self._chunksize = chunksize
        self._Bstruct = Bstruct

    def delete(self):
        del self._Bstruct.data_grp[self._h5_dataset_key]

    def __getitem__(self, item):
        my_datatypes: BatchDatatypHolder = self.getDatatypes()
        if BatchDatatypClass.PYTHON_OBJECT in my_datatypes or BatchDatatypClass.NUMPY_STRING in my_datatypes:

            my_datatypes.removeAllnoneObject()
            requested_data = self._Bstruct.data_grp[self._h5_dataset_key].__getitem__(item)

            if isinstance(item, tuple):
                for elem in item:
                    if elem in my_datatypes:
                        self._convertLISTBack2Object(requested_data[elem])

            elif isinstance(item, int):
                if my_datatypes.is_flat():
                    for i,_ in enumerate(requested_data):
                        requested_data[i] = pickle.loads(base64.b64decode(requested_data[i]))
                else:
                    object_cols = my_datatypes.getColumns()
                    for item in object_cols:
                        requested_data[item] = pickle.loads(base64.b64decode(requested_data[item]))

            elif isinstance(item, list) or isinstance(item, np.ndarray):
                if my_datatypes.is_flat():
                    self._convertLISTBack2Object(requested_data)
                else:
                    object_cols = my_datatypes.getColumns()
                    for item in object_cols:
                        self._convertLISTBack2Object(requested_data[item])

            elif isinstance(item, slice):
                if my_datatypes.is_flat():
                    self._convertLISTBack2Object(requested_data)
                else:
                    object_cols = my_datatypes.getColumns()
                    for item in object_cols:
                        self._convertLISTBack2Object(requested_data[item])

            elif isinstance(item, str):
                if item in my_datatypes:
                    self._convertLISTBack2Object(requested_data)

            return requested_data
        else:
            requested_data = self._Bstruct.data_grp[self._h5_dataset_key].__getitem__(item)
        return requested_data

    def get_notConverted(self, slice):
        requested_data = self._Bstruct.data_grp[self._h5_dataset_key].__getitem__(slice)
        return requested_data

    def getColumns(self):
        my_datatypes: BatchDatatypHolder = self.getDatatypes()
        return my_datatypes.getColumns()

    def _convertLISTBack2Object(self, listof):
        for i, item in enumerate(listof):
            if isinstance(item, np.ndarray):
                for j, row in enumerate(item):
                    if len(item) > 0:
                        listof[i][j] = pickle.loads(base64.b64decode(row))
                    else:
                        listof[i][j] = None
            else:
                if len(item) > 0:
                    listof[i] = pickle.loads(base64.b64decode(item))
                else:
                    listof[i] = None

    def reorder(self, split: "Split", new_tableName) -> ("BatchTable", "Split"):
        return self._Bstruct.partition.createSubset_reorder(self, split, new_tableName)

    def __iter__(self):
        return Batch_Access(self._Bstruct, self, self._h5_dataset_key, self._chunksize)

    def __len__(self):
        return len(self._Bstruct.data_grp[self._h5_dataset_key])

    def __repr__(self):
        if len(self) > 0:
            if len(self) > 2:
                return f'dtyp: {self.getDatatypes()} |0: {str(self._shortenArrayPrint(self[0]))} \n 1: {self._shortenArrayPrint(self[1])} \n ...'
            else:
                return f'dtyp: {self.getDatatypes()} |0: {str(self._shortenArrayPrint(self[0]))} \n ...'
        return f'BatchTable len <= 0 '

    def _shortenArrayPrint(self, arr: np.ndarray):
        if len(arr) > 1:
            return f'[{arr[0]} ; ... ; {arr[-1]}]'
        else:
            return f'[{arr[0]}]'

    def getDatatypes(self) -> BatchDatatypHolder:
        db = self._Bstruct.data_grp[self._h5_dataset_key]
        att_value = db.attrs['dtyps']
        return pickle.loads(base64.b64decode(att_value))

    def getChunksize(self):
        return self._chunksize

    def createShadowTable(self, indicies: List[int]) -> "Batch_ShadowTable":
        return Batch_ShadowTable(indicies, self)

    def optimizeAccess(self, indicies: List[int]):
        raise Exception('Not implemented yet')

    def getWith(self):
        count: int = 0
        if len(self) > 0:
            dtype_list = self.getDatatypes()

            for dtyp in dtype_list:
                dtyp = dtype_list[dtyp]
                if dtyp.get_shape() is None:
                    count += 1
                elif len(dtyp.get_shape()) == 0:
                    count += 1
                elif len(dtyp.get_shape()) == 1:
                    count += dtyp.get_shape()[0]
                else:
                    raise Exception('find a dtyp with a 2D data shape. That is not support!')

            return count
        else:
            return 0

    def flattBatchTable(self, name: str = None):
        if name is None:
            # override
            iterator: Batch_Access = iter(self)
            batch: np.ndarray
            dataTypHolder: BatchDatatypHolder = self.getDatatypes()

            if dataTypHolder.checkAllsame():
                datatyp = dataTypHolder[dataTypHolder.getColumns()[0]]
                datatyp.set_shape((self.getWith(),))

                for batch in iterator:
                    out = np.empty(shape=(len(batch),),dtype=datatyp.toNUMPY())
                    self._flat(batch, out)
                    iterator <<= out
            else:
                raise Exception('different Types are not supported at the moment')
        else:
            raise Exception('create new is not supported at the moment')

    def convert_2_ndarray(self, batch_index=-1):
        # override
        iterator: Batch_Access = iter(self)
        batch: np.ndarray
        dataTypHolder: BatchDatatypHolder = self.getDatatypes()

        if dataTypHolder.checkAllsame():
            datatyp = dataTypHolder[dataTypHolder.getColumns()[0]]
            datatyp.set_shape(None)

            np_dtype = dataTypHolder.toNUMPY_dtypes(False)
            #np_dtype = np.dtype([('SM1', np.str),('SM2', np.str)])
            shape = (len(self), self.getWith())

            if datatyp == BatchDatatypClass.NUMPY_STRING:
                if batch_index == -1:
                    data = np.array(self[:].tolist())
                    return data
                else:
                    return np.array(self.get_index(batch_index).tolist())
            else:
                if batch_index == -1:
                    return self[:].view(dtype=np_dtype).reshape(shape)
                else:
                    return self.get_index(batch_index).view(dtype=np_dtype).reshape(shape)
        else:
            raise Exception('different Types are not supported at the moment')


    def _flat(self, batch: np.ndarray, out: np.ndarray):
        if len(batch) == 0:
            raise Exception('batch is empty')

        dataTypHolder: BatchDatatypHolder = self.getDatatypes()
        datatyp = dataTypHolder[dataTypHolder.getColumns()[0]]


        cols = self.getColumns()
        entry_counter = 0
        batch_splits = []

        for col in cols:
            if len(batch_splits) == 0:
                try:
                    if datatyp == BatchDatatypClass.NUMPY_STRING:
                        split = (0, 1)
                        entry_counter += 1
                    else:
                        split = (0, len(batch[col][0]))
                except:
                    # if col is not an ndarray
                    split = (0, 1)
            else:
                try:
                    if datatyp == BatchDatatypClass.NUMPY_STRING:
                        split = (entry_counter, entry_counter+1)
                        entry_counter += 1
                    else:
                        split = (batch_splits[-1][1], batch_splits[-1][1] + len(batch[col][0]))
                except:
                    # if col is not an ndarray
                    split = (batch_splits[-1][1], batch_splits[-1][1] + 1)

            batch_splits.append(split)

        for i, entry in enumerate(batch):
            for col_i, col in enumerate(cols):
                if len(out.shape) == 1:
                    out[i] = entry[col]
                else:
                    out[i][batch_splits[col_i][0]:batch_splits[col_i][1]] = entry[col]

    def get_index(self, index: int) -> np.ndarray:
        start = index * self._chunksize
        end = ((self._last_index + 1) * self._chunksize)

        if end >= len(self._BTable):
            end = len(self._BTable)

        data = self[start:end]

        return data


class Batch_Access:
    _last_index: int
    _Bstruct: 'BatchStructure'
    _BTable: BatchTable
    _chunksize: int
    _writeBackNeeded = False
    _h5_keyname: str

    def __init__(self, Bstruct: 'BatchStructure', BTable: BatchTable, h5_keyname, chunksize, _last_index=-1):
        self._last_index = _last_index
        self._Bstruct = Bstruct
        self._chunksize = chunksize
        self._writeBackNeeded = False
        self._h5_keyname = h5_keyname
        self._BTable = BTable

    def __iter__(self):
        return self

    def _getDB(self):
        return self._Bstruct.data_grp[self._h5_keyname]

    # @benchmark_function
    def __next__(self) -> h5py.Dataset:
        self._last_index += 1
        if self._last_index >= self.batchcount():
            if self._writeBackNeeded:
                self.writeBack()
            raise StopIteration

        start = self._last_index * self._chunksize
        end = ((self._last_index + 1) * self._chunksize)

        if end >= len(self._BTable):
            end = len(self._BTable)

        data = self._BTable[start:end]

        return data

    def batchcount(self):
        chunks = math.ceil(float(len(self._BTable)) / float(self._chunksize))
        return chunks

    def __len__(self):
        return self.batchcount()

    def last_index(self):
        return self._last_index

    # @benchmark_function
    def __lshift__(self, other):
        if self._writeBackNeeded:
            raise Exception('dtypes of the batch are change during the process :(')

        if not isinstance(other, np.ndarray):
            raise Exception('the passed batch is not a numpy array')
        other: np.array = other

        dtyp = self._BTable.getDatatypes()
        if not dtyp == BatchDatatypHolder().fromNUMPY_dtyp(other.dtype):
            #check for string object problematic
            if not dtyp.toNUMPY_dtypes() == other.dtype:
                raise Exception('the dtypes of the numpy arrays is not the same as in the batchtable')

        if self._last_index >= self.batchcount():
            raise Exception('index is equal or higher than batchcount')

        if self._writeBackNeeded:
            raise Exception('mixed some overrider methods <<= and <<')

        return self._fastoverride(other, self._last_index)

    def _fastoverride(self, data, index):
        start = index * self._chunksize
        end = ((index + 1) * self._chunksize)

        if end >= len(self._BTable):
            end = len(self._BTable)

        self._getDB()[start:end] = data
        return self

    # @benchmark_function
    def __ilshift__(self, other):
        if not isinstance(other, np.ndarray):
            raise Exception('the passed batch is not a numpy array')
        other: np.array = other

        if self._last_index >= self.batchcount():
            raise Exception('index is equal or higher than lenBatch')

        name = f'batchTMP_{hex(id(self))}'
        if name not in self._Bstruct.tmp_grp.keys():
            shape = len(self._BTable)
            dtype = other.dtype
            chunksize = self._chunksize

            if chunksize > len(self._BTable):
                chunksize = len(self._BTable)

            dataTypHolder = BatchDatatypHolder().fromNUMPY_dtyp(dtype)
            if len(dataTypHolder) == 1 and len(dataTypHolder[dataTypHolder.getColumns()[0]].get_shape()) == 0 and len(other.shape) > 1:
                new_shape = list(other.shape)
                new_shape[0] = len(self._BTable)
                new_shape = tuple(new_shape)
                self._Bstruct.partition.createDatabase(name, dataTypHolder, new_shape, chunksize=chunksize,
                                                       inTMP=True)
            else:
                self._Bstruct.partition.createDatabase(name, dataTypHolder, shape, chunksize=chunksize, inTMP=True)

            dataTypHolder.removeAllnoneObject()

            start = 0
            end = self._chunksize

            if end >= len(self._BTable):
                end = len(self._BTable)

            self._writeBackNeeded = True
            self._convert_pickelObjects(other, columns=dataTypHolder.getColumns(), flat=dataTypHolder.is_flat())
            self._Bstruct.tmp_grp[name][start:end] = other
        else:
            start = self._last_index * self._chunksize
            end = ((self._last_index + 1) * self._chunksize)

            if end >= len(self._BTable):
                end = len(self._BTable)

            if not self._writeBackNeeded:
                raise Exception('dtypes of the batch are change during the process :(')

            dtype = other.dtype

            dataTypHolder = BatchDatatypHolder().fromNUMPY_dtyp(dtype)
            dataTypHolder.removeAllnoneObject()
            self._convert_pickelObjects(other, columns=dataTypHolder.getColumns(), flat=dataTypHolder.is_flat())
            self._Bstruct.tmp_grp[name][start:end] = other

        return self

    def writeBack(self):
        name = f'batchTMP_{hex(id(self))}'
        new_db = self._Bstruct.tmp_grp[name]
        del self._Bstruct.data_grp[self._h5_keyname]
        self._Bstruct.data_grp.move(new_db.name, self._h5_keyname)

    def _convert_pickelObjects(self, arr: np.ndarray, columns: List[str], flat=False):
        if not flat:
            for i, row in enumerate(arr):
                for col in columns:
                    arr[i][col] = base64.b64encode(pickle.dumps(arr[i][col], protocol=pickle.HIGHEST_PROTOCOL))
        elif len(columns) > 0:
            if len(arr.shape) > 1 and arr.shape[1] > 1:
                for i, row in enumerate(arr):
                    for j in range(arr.shape[1]):
                        arr[i][j] = base64.b64encode(pickle.dumps(arr[i][j], protocol=pickle.HIGHEST_PROTOCOL))
            else:
                for i, row in enumerate(arr):
                    arr[i] = base64.b64encode(pickle.dumps(arr[i], protocol=pickle.HIGHEST_PROTOCOL))



class Batch_ShadowTable:
    _indicies: List[int]
    _batchtable: BatchTable

    def __init__(self, indicies: List[int], batchtable: BatchTable):
        self._indicies = indicies
        self._batchtable = batchtable

    def __getitem__(self, item):
        return self._batchtable[self._indicies[item]]

    def __len__(self):
        return len(self._indicies)
