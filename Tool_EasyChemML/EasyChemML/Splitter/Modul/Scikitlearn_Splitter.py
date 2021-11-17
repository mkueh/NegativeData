from sklearn.ensemble.tests.test_gradient_boosting import test_warm_start_oob_switch
from sklearn.model_selection import KFold, ShuffleSplit


class Scikitlearn_Splitter(object):

    def __init__(self):
        pass

    @staticmethod
    def regSplitter():
        return ['s_kfold', 's_shuffle']

    def split(self, train_raw, **kwargs):
        if not 'splitter' in kwargs:
            raise ValueError('splitter is not set')

        splitter = kwargs['splitter']

        if splitter == 's_kfold':
            return self.__Kfold(train_raw, **kwargs)
        elif splitter == 's_shuffle':
            return self.__shuffleSplit(train_raw, **kwargs)

        pass

    def __Kfold(self, train_raw, **kwargs):
        arg = kwargs.copy()
        del arg['splitter']
        del arg['raw_column']
        return self.__sptoarr(KFold(**arg).split(train_raw))

    def __shuffleSplit(self, train_raw, **kwargs):
        arg = kwargs.copy()
        del arg['splitter']
        del arg['raw_column']
        return self.__sptoarr(ShuffleSplit(**arg).split(train_raw))

    """
    Get the SplitterIndieces and return
    """

    def __sptoarr(self, split):
        arr = []
        for f, (x, y) in enumerate(split):
            arr.append((x, y))  # first train than test
        return arr

    @staticmethod
    def getItemname():
        return 'scikit_splitter'
