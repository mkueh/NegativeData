from EasyChemML.Splitter.Splitcreator import Splitset
from EasyChemML.Utilities.DataUtilities.BatchTable import BatchTable
from EasyChemML.Utilities.DataUtilities.BatchPartition import BatchPartition

from typing import List, Dict

class Additionaldata_Payload(object):

    payload_name:str = ''

    _feature_key:str = -1
    _feature_encoded:List[str] = -1
    _target_key:str = -1

    _splits: Splitset = None

    def __init__(self, name:str, feature_key:str = '', feature_encoded:List[str] = [], target_key:str = '', splits:Splitset = None):
        self.payload_name = name

        self._feature_key = feature_key
        self._feature_encoded = feature_encoded
        self._target_key = target_key

        self._splits = splits

class Dataset(object):
    _feature_key = -1
    _target_key = -1
    _splits: Splitset = None

    _outputfolder: str = None
    _TMP_FOLDER: str = None

    name: str = None
    _encodingColumns: Dict[str, Dict]
    _batch_partition:BatchPartition = -1

    _additionaldata_payload:List[Additionaldata_Payload]

    def __init__(self, feature_key:str = '', target_key:str='', split:Splitset=None, name='noname', workingfolder=None,
                 TMP_FOLDER=None, encodingColumns=None, batch_partition=None, additionaldata_payload: Dict[str, Dict]=None):
        self._additionaldata_payload = additionaldata_payload

        self._feature_key = feature_key
        self._target_key = target_key
        self._splits = split
        self._outputfolder = workingfolder

        self._encodingColumns = encodingColumns
        self._batch_partition = batch_partition
        self._TMP_FOLDER = TMP_FOLDER
        self.name = name

    def getTMP_FOLDER(self):
        return self._TMP_FOLDER

    def setTMP_FOLDER(self, TMP_FOLDER) -> str:
        self._TMP_FOLDER(TMP_FOLDER)

    def getEncoding_Columns(self) -> List[str]:
        return self._encodingColumns

    def getBatchPartition(self) -> BatchPartition:
        return self._batch_partition

    def getFeature_key(self) -> str:
        return self._feature_key

    def getTarget_key(self) -> str:
        return  self._target_key

    def getFeature_data(self) -> BatchTable:
        return self._batch_partition[self._feature_key]

    def getTargets_data(self) -> BatchTable:
        return self._batch_partition[self._target_key]

    def getSplits(self) -> Splitset:
        return self._splits

    def getOutputFolder(self) -> str:
        return self._outputfolder

    def setBatchPartition(self, batch_partition:BatchPartition):
        self._batch_partition = batch_partition

    def setEncoding_Columns(self, encoding_columns:List[str]):
        self._encodingColumns = encoding_columns

    def setFeature_key(self, feature_key):
        self._feature_key = feature_key

    def setTarget_key(self, target_key):
        self._target = target_key

    def setSplits(self, split: Splitset):
        self._splits = split

    def setOutputFolder(self, outputfolder: str):
        self._outputfolder = outputfolder

    def get_additionaldata_payload(self):
        return self._additionaldata_payload

    def set_additionaldata_payload(self, additionaldata_payload:Dict[str,Additionaldata_Payload]):
        self._additionaldata_payload = additionaldata_payload
