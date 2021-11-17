from enum import Enum, auto
from typing import List
import numpy as np


class HyparameterTyp(Enum):
    Categorical = auto()
    Int_range = auto()
    Float_range = auto()


class IntRange:
    start: int
    end: int
    step: int
    count: int

    def __init__(self, start: int = 0, end: int = 0, step: int = 1, count: int = None):
        self.start = start
        self.end = end
        self.step = step
        self.count = count

    def generateExplicit(self):
        arr = []

        if not self.count is None:
            raise Exception('It is not possible to find an explicit representation for this hyperparameter if count is set.')

        return list(np.arange(start=self.start, stop=self.end, step=self.step))

class FloatRange:
    start: float
    end: float
    step: float
    count: int

    def __init__(self, start: float = 0.0, end: float = 0.0, step: float = 1, count: int = None):
        self.start = start
        self.end = end
        self.step = step
        self.count = count

    def generateExplicit(self):
        arr = []

        if not self.count is None:
            raise Exception('It is not possible to find an explicit representation for this hyperparameter if count is set.')

        return list(np.arange(self.start, self.end, self.step))


class Categorically:
    items: List

    def __init__(self, items):
        self.items = items


class HyperParameter:
    _type: HyparameterTyp
    _obj: object

    def __init__(self, para_config: dict):
        self._type = self._getTyp(para_config['typ'])
        if self._type == HyparameterTyp.Categorical:
            self._obj = self._getObj(para_config['items'])
        elif self._type == HyparameterTyp.Int_range:
            self._obj = self._getObj(para_config['range'])
        elif self._type == HyparameterTyp.Float_range:
            self._obj = self._getObj(para_config['range'])

        if self._type == HyparameterTyp.Int_range or self._type == HyparameterTyp.Float_range:
            if 'count' in para_config:
                self._obj.count = para_config['count']


    def _getTyp(self, typ: str):
        if typ == 'cat':
            return HyparameterTyp.Categorical
        elif typ == 'int':
            return HyparameterTyp.Int_range
        elif typ == 'flt':
            return HyparameterTyp.Float_range

    def _getObj(self, data: dict):
        if self._type == HyparameterTyp.Categorical:
            return Categorically(data)

        elif self._type == HyparameterTyp.Int_range:
            if len(data) == 3:
                return IntRange(data[0], data[1], data[2])
            elif len(data) == 2:
                return IntRange(data[0], data[1])
            else:
                raise Exception('Hyperparameter could not be created! Integer range is defined incorrectly')

        elif self._type == HyparameterTyp.Float_range:
            if len(data) == 3:
                return FloatRange(data[0], data[1], data[2])
            elif len(data) == 2:
                return FloatRange(data[0], data[1])
            else:
                raise Exception('Hyperparameter could not be created! Float range is defined incorrectly')

    """
    Useful for gridsearch
    """
    def generateExplicitList(self):
        if self._type == HyparameterTyp.Categorical:
            return self._obj.items
        else:
            return self._obj.generateExplicit()

    def getTyp(self):
        return self._type


    def getHyperparamter(self):
        return self._obj
