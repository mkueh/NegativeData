# distutils: language=c++
# cython: language_level=3

import copy
from rdkit import Chem
from rdkit.Avalon import pyAvalonTools
from rdkit.Chem import MACCSkeys, AllChem
from rdkit.Chem import rdMolDescriptors
from rdkit.DataStructs.cDataStructs import ExplicitBitVect
from libcpp.vector cimport vector
from libcpp cimport bool
from typing import List

cdef class FingerprintGenerator(object):

    def __init__(self):
        #print("FingerprintGenerator geladen")
        pass

    def generateArrofFingerprints(self, data, fingerprints:list, args:list):
        outputList = []
        cdef vector[char] col_tmp
        cdef vector[char] tmp
        for item in data:
            tmp_args = copy.deepcopy(args)

            for i, fp_name in enumerate(fingerprints):
                if 'length' in tmp_args[i]:
                    length = tmp_args[i]['length']
                    del tmp_args[i]['length']
                else:
                    if not fp_name == 'maccs':
                        raise Exception('Length not setten in args nr. ' + str(i) + f' | fp_name: {fingerprints[i]}')

                tmp = vector[char]()
                if fp_name == 'rdkit':
                    tmp = self.__generateFingerprints_RDKit(item, length, tmp_args[i])
                elif fp_name == 'morgan_circular':
                    tmp = self.__generateFingerprints_Morgan_Circular(item, length, tmp_args[i])
                elif fp_name == 'avalon':
                    tmp = self.__generateFingerprints_Avalon(item, length, tmp_args[i])
                elif fp_name == 'layerdfingerprint':
                    tmp = self.__generateFingerprints_LayerdFingerprint(item, length, tmp_args[i])
                elif fp_name == 'maccs':
                    tmp = self.__generateFingerprints_MACCS_keys(item, tmp_args[i])
                elif fp_name == 'atom_pairs':
                    tmp = self.__generateFingerprints_Atom_Pairs(item, length, tmp_args[i])
                elif fp_name == 'topological_torsions':
                    tmp = self.__generateFingerprints_Topological_Torsions(item, length, tmp_args[i])
                else:
                    raise Exception(f'The selected fingerprintname is not supported {fp_name}')
                col_tmp.insert(col_tmp.end(), tmp.begin(), tmp.end())

            outputList.append(col_tmp)
            col_tmp = vector[char]()

        return outputList


    cpdef vector[bool] __generate_boolArray(self, fp: ExplicitBitVect):
        convert2String = fp.ToBitString()
        cdef vector[bool] bitarray
        bitarray.resize(len(convert2String))

        for i,c in enumerate(convert2String):
            if c == '1':
                bitarray[i] = 1 #True
            else:
                bitarray[i] = 0 #False

        return bitarray

    cdef vector[bool] __getEmptyBitVector(self, int length):
        cdef vector[bool] outputVector
        outputVector.resize(length)

        for i, _ in enumerate(outputVector):
            outputVector[i] = 0

        return outputVector

    def __generateFingerprints_RDKit(self, data, length, args):
        if data == 'NA':
            return self.__getEmptyBitVector(length)
        fp = Chem.RDKFingerprint(mol=data, fpSize=length, **args)
        return self.__generate_boolArray(fp)

    def __generateFingerprints_Atom_Pairs(self, data, length, args):
        if data == 'NA':
            return self.__getEmptyBitVector(length)
        return self.__generate_boolArray(rdMolDescriptors.GetHashedAtomPairFingerprintAsBitVect(data, nBits=length, **args))

    def __generateFingerprints_Topological_Torsions(self, data, length, args):
        if data == 'NA':
            return self.__getEmptyBitVector(length)
        return self.__generate_boolArray(rdMolDescriptors.GetHashedTopologicalTorsionFingerprintAsBitVect(data, nBits=length, **args))

    def __generateFingerprints_MACCS_keys(self, data, args):
        if data == 'NA':
            return self.__getEmptyBitVector(167)
        return self.__generate_boolArray(MACCSkeys.GenMACCSKeys(data, **args))

    def __generateFingerprints_Morgan_Circular(self, data, length , args):
        if data == 'NA':
            return self.__getEmptyBitVector(length)
        return self.__generate_boolArray(AllChem.GetMorganFingerprintAsBitVect(data, nBits=length, **args))

    def __generateFingerprints_Avalon(self, data, length, args):
        if data == 'NA':
            return self.__getEmptyBitVector(length)
        return self.__generate_boolArray(pyAvalonTools.GetAvalonFP(data, nBits=length, **args))

    def __generateFingerprints_LayerdFingerprint(self, data, length, args):
        if data == 'NA':
            return self.__getEmptyBitVector(length)
        return self.__generate_boolArray(Chem.LayeredFingerprint(data, fpSize=length, **args))