import os, argparse, hjson, copy, pandas, shutil
from typing import List, Dict
from itertools import groupby, product

class Ex_Config():

    paths:List
    configs:List
    groupID:int

    def __init__(self, paths, configs, groupID):
        self.paths = paths
        self.configs = configs
        self.groupID = groupID

class HyperConfig():

    type: str
    group: int
    items: List

    path: List[str]

    def __init__(self, config:Dict, path):
        self.typ = config['type']
        self.group = config['group']
        self.items = config['items']
        self.path = path

    def __len__(self):
        return len(self.items)

class HyperGroup():

    Hyperconfigs:List[HyperConfig]
    groupID: int

    def __init__(self, Configs:List[HyperConfig]):
        self.Hyperconfigs = Configs
        self.groupID = Configs[0].group
        self._precheck()

    def _precheck(self):
        length = len(self.Hyperconfigs[0])
        for config in self.Hyperconfigs:
            if not length == len(config):
                raise Exception(f'Hyperconfigs in one Groupe have not the same size! {self.groupID}')

    def create_Configs(self) -> List[Ex_Config]:
        Ex_Configs = []
        for i in range(len(self.Hyperconfigs[0])):
            exc = Ex_Config([], [], self.groupID)

            for config in self.Hyperconfigs:
                exc.configs.append(config.items[i])
                exc.paths.append(config.path)

            Ex_Configs.append(exc)
        return Ex_Configs



"""
Folgende Parameter in der settings.json sind möglich 

{val:'hyperconfig', type:'fix', group: 1, items:[]}
geht an jeder stelle solange der Pfad nur aus dicts besteht

Folgende Parameter werden in der submit ersetzt

%CONFIG_NAME% : wird zum Confignamen
%PATH_CONFIG% : wird zum Pfad der zur settings.hjson fuehrt

"""
def main(configpath, submitpath):
    hyper_hjson = _loadHjson(configpath)
    working_dir = '//'.join(configpath.split('/')[0:-1])

    #Generiere Hyperconfigs
    Hyperconfigs = _scan_configDict(hyper_hjson, [])
    #Sortieren und gruppieren
    Hyperconfigs.sort(key=lambda x: x.group, reverse=False)
    grouped = [list(g) for k, g in groupby(Hyperconfigs, lambda s: s.group)]

    HyperGroups:List[HyperConfig] = []
    for group in grouped:
        HyperGroups.append(HyperGroup(group))

    #Explizite Configs erstellen und gruppieren
    Ex_Configs:List[Ex_Config] = []
    for group in HyperGroups:
        Ex_Configs.extend(group.create_Configs())
    Ex_Configs.sort(key=lambda x: x.groupID, reverse=False)
    groupedBYID = [list(g) for k, g in groupby(Ex_Configs, lambda s: s.groupID)]
    exparas_grouped = list(product(*groupedBYID))

    #Jeden Hyperparameter Durchgang generieren
    replace_configs = []
    for i,groups in enumerate(exparas_grouped):
        tmp = Ex_Config([],[], -1)
        for group in groups:
            tmp.paths.extend(group.paths)
            tmp.configs.extend(group.configs)
        exparas_grouped[i]= tmp

    #default dict mit expliziten Paramtern ueberschreiben
    configs = []
    dataframe: pandas.DataFrame = pandas.DataFrame()
    for i, item in enumerate(exparas_grouped):
        configs.append(_rekonstructDict(item, copy.deepcopy(hyper_hjson)))

        tmp_list = [[f'CONFIG_{i}'],item.paths, item.configs, []]
        dataframe = dataframe.append(pandas.DataFrame(tmp_list))

    dataframe.to_excel("CONFIG_info.xlsx", engine='openpyxl')


    for i, config in enumerate(configs):
        if os.path.exists(f'CONFIG_{i}'):
            shutil.rmtree(f'CONFIG_{i}')
        os.mkdir(f'CONFIG_{i}')
        h_json = os.path.join(f'CONFIG_{i}', f'settings.hjson')
        _dumpHjson(config, h_json)

        cmd_path = os.path.join(f'CONFIG_{i}', f'submit.cmd')
        h_json = '//'.join(h_json.split('/')[0:-1])
        createSubmitcmd(cmd_path, submitpath, os.path.abspath(h_json), f'CONFIG_{i}')

def createSubmitcmd(path, submitpath, config_path, config_name):
    default = open(submitpath, "r")
    newone = open(path, "w")

    for row in default:
        if '%CONFIG_NAME%' in row or '%PATH_CONFIG%' in row:
            replaced = row.replace('%CONFIG_NAME%', config_name)
            replaced = replaced.replace('%PATH_CONFIG%', config_path)
            newone.write(replaced)
        else:
            newone.write(row)

def _loadHjson(path) -> dict:
    if os.path.exists(path):
        with open(path, 'r', encoding='utf8') as json_file:
            data = hjson.load(json_file)
        return data
    else:
        raise Exception('Configloader can not find the file')

def _dumpHjson(dic, path) -> dict:
    with open(path, 'w', encoding='utf8') as json_file:
        data = hjson.dump(dic,json_file)
    return data

def _scan_configDict(hyper_hjson:dict, lst_path):
    config:List[HyperConfig] = []
    current_path = copy.copy(lst_path)
    current_path.append('')
    for key in hyper_hjson:
        current_path[-1] = key
        if isinstance(hyper_hjson[key], dict):
            if 'val' in hyper_hjson[key] and hyper_hjson[key]['val'] == 'hyperconfig':
                config.append(HyperConfig(hyper_hjson[key], copy.copy(current_path)))
            else:
                config.extend(_scan_configDict(hyper_hjson[key], copy.copy(current_path)))
    return config

def _rekonstructDict(exparas:Ex_Config, overide_hyperJson):
    exparas:Ex_Config
    for j, path in enumerate(exparas.paths):
        _rekusivConstraction(path, exparas.configs[j], overide_hyperJson)

    return overide_hyperJson

def _rekusivConstraction(paths:List[str], set_config, old_dict:Dict):
    if len(paths) == 1:
        old_dict[paths[0]] = set_config
    else:
        if paths[0] in old_dict:
            _rekusivConstraction(paths[1:], set_config, old_dict[paths[0]])
        else:
            old_dict[paths[0]] = {}
            _rekusivConstraction(paths[1:], set_config, old_dict[paths[0]])

    return old_dict

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", "-cf", help="Path to config file")
    parser.add_argument("--submit_file", "-sf", help="Path to default submit file")
    args = parser.parse_args()
    main(args.config_file, args.submit_file)



