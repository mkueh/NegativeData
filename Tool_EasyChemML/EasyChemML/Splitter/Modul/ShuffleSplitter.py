from enum import Enum
from sortedcontainers import SortedList
import random, numpy as np


class Modus(Enum):
    splitby_train = 1
    splitby_test = 2
    notset = -1


class ShuffleSplitter(object):

    def __init__(self):
        pass

    def split(self, data, **kwargs):
        modus: Modus = Modus.notset
        value = -1
        n_splits = -1
        if 'random_state' in kwargs:
            np.random.seed(kwargs['random_state'])

        if not 'test_size' in kwargs and not 'train_size' in kwargs:
            raise ValueError('you need to set test_size or train_size')
        elif not 'train_size' in kwargs and 'test_size' in kwargs:
            modus = Modus.splitby_test
            value = kwargs['test_size']
        elif 'train_size' in kwargs and not 'test_size' in kwargs:
            modus = Modus.splitby_train
            value = kwargs['train_size']
        elif 'train_size' in kwargs and 'test_size' in kwargs:
            raise ValueError('you can only set one of test_size or train_size')
        if not 'n_splits' in kwargs:
            raise ValueError('n_splits is not set')

        if not isinstance(value, float):
            raise ValueError('testset_start or testset_end is not a float')

        if not (value > 0 and value < 1):
            raise ValueError('testset_start or testset_end is bigger and equals than 1 or smaller or equals than 0')

        n_splits = kwargs['n_splits']
        data_length = len(data)

        splits = self._splitBy(n_splits, data_length, value)
        for i, split in enumerate(splits):
            splits[i] = self._create_traintest_tupel(modus, split, data_length)
            # if not self._preCheck(splits[i][0],splits[i][1]):
            #    raise Exception('DATA LEAKAGE')
        return splits

    def _splitBy(self, n_splits, data_length, test_size):
        out = []
        test_count = int(data_length * test_size)

        for split in range(n_splits):
            out.append(self._createRandomIndexList(test_count, data_length))
        return out

    def _preCheck(self, list_1, list_2):
        for item in list_1:
            if item in list_2:
                return False
        return True

    def _create_traintest_tupel(self, modus: Modus, split, max_size):
        if modus == Modus.splitby_test:
            train = [item for item in list(range(0, max_size)) if item not in split]
            train = np.sort(train)
            return (train, split)
        elif modus == Modus.splitby_train:
            test = [item for item in list(range(0, max_size)) if item not in split]
            test = np.sort(test)
            return (split, test)

    def _createRandomIndexList(self, length, max_size):
        sl = SortedList()

        counter = 0
        while True:
            if counter >= length:
                return list(sl)

            random_int = np.random.randint(low=0, high=max_size)
            if not random_int in sl:
                sl.add(random_int)
                counter += 1

    @staticmethod
    def getItemname():
        return 's_shuffle'
