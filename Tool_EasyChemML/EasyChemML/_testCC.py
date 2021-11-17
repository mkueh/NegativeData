from HyperparameterSearch.Config_Creator import Config_Creator
from ModulSystem.ModulManager import ModulManager


MManger = ModulManager()
CC = Config_Creator(MManger)
C = CC.createConfiguration(None, 'scikit_randomforest_r', {'n_estimators': {'typ':'cat', 'items':[100,1000,10000]},'random_state':42,'n_jobs': -2})

print(C)
