class PresetSplitter(object):

    def __init__(self):
        pass

    def split(self, train_raw, **kwargs):
        out = list()
        if not 'testset_start' in kwargs:
            raise ValueError('testset_start is not set')
        if not 'testset_end' in kwargs:
            raise ValueError('testset_end is not set')

        testset = list(range(int(kwargs['testset_start']), int(kwargs['testset_end'])))
        trainset = [item for item in list(range(0,len(train_raw))) if item not in testset]
        out.append((trainset, testset))
        return out

    @staticmethod
    def getItemname():
        return 's_preset'
    