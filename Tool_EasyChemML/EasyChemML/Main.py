from EasyChemML.AFE_DM import AFE_DM
import os, argparse, glob, sys, shutil, json
import logging, time

from EasyChemML.Configuration.Configloader import Configloader
from EasyChemML.Utilities.Application_env import Application_env
from EasyChemML.ModulSystem.ModulManager import ModulManager
from EasyChemML.Utilities.MetricUtilities.MetricFabricator import MetricFabricator

needed_data = [("settings.hjson", "default_settings.hjson")]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workingdir", "-w", help="set the working-folder")
    parser.add_argument("--clean", '-c', action='store_const', const=False, help="not clean Output folder before start")
    parser.add_argument("--initialize", "-init", action='store_const', const=True,
                        help="initialize the current folder or the one that was set by -w")
    args = parser.parse_args()

    initialize = args.initialize
    workingdir = args.workingdir
    clean = args.clean

    if initialize and workingdir:
        __init(workingdir)

    elif initialize:
        __init(os.getcwd())

    elif workingdir:
        rank = 0
        workingPath = workingdir
        if os.path.exists(os.path.join(workingPath, 'TMP')):
            print('remove TMP')
            shutil.rmtree(os.path.join(workingPath, 'TMP'))

        if not rank == 0:
            hjsonfiles = __getAllHJSON(workingPath)
            for file in needed_data:
                if not file[0] in hjsonfiles:
                    print('Folder not contain a needed file: ' + str(file[0]))
                    return
        __runME(workingPath, rank, clean)

    else:
        rank = 0
        workingPath = os.getcwd()

        if not rank == 0:
            hjsonfiles = __getAllHJSON(workingPath)
            for file in needed_data:
                if not file[0] in hjsonfiles:
                    print('Folder not contain a needed file: ' + str(file[0]))
                    print('you can use -init to initialize the working-folder')
                    return
        __runME(workingPath, rank, clean)


def __init(path):
    programm_path, file = os.path.split(sys.argv[0])
    configfile = os.path.join(programm_path, 'default_settings.hjson')
    target = os.path.join(path, 'settings.hjson')
    shutil.copyfile(configfile, target)


def __runME(workingPath, rank, clean):
    from importlib import reload
    reload(logging)

    cleanUpWorkdir(workingPath, clean, True)
    OutputPath = os.path.join(workingPath, 'Output')
    if not os.path.exists(OutputPath):
        print('Output folder not found ... i create one for you')
        os.mkdir(OutputPath)

    current_path = os.path.dirname(__file__)
    version_path = os.path.join(current_path, "Version.json")
    if os.path.exists(version_path):
        with open(version_path, "r") as file:
            json_dict = json.load(file)
            version_hash = json_dict['hash']
            compile_date = json_dict['time']
    else:
        version_hash = None
        compile_date = None

    print(' ###################################################################################')
    print('    ______           _______     _______ _    _ ______ __  __        __  __ _       ')
    print('   |  ____|   /\    / ____\ \   / / ____| |  | |  ____|  \/  |      |  \/  | |      ')
    print('   | |__     /  \  | (___  \ \_/ / |    | |__| | |__  | \  / |______| \  / | |      ')
    print('   |  __|   / /\ \  \___ \  \   /| |    |  __  |  __| | |\/| |______| |\/| | |      ')
    print('   | |____ / ____ \ ____) |  | | | |____| |  | | |____| |  | |      | |  | | |____  ')
    print('   |______/_/    \_\_____/   |_|  \_____|_|  |_|______|_|  |_|      |_|  |_|______| ')
    print('                                                                                    ')
    print('####################################################################################')

    path_settings = os.path.join(workingPath, 'settings.hjson')
    config = Configloader(path_settings)
    Lsettings = config.getLearningsettings()
    Lsettings.workingPath = workingPath

    logging.basicConfig(filename=os.path.join(OutputPath, 'MainNode.log'), level=logging.INFO)

    logging.info(' ###################################################################################')
    logging.info('    ______           _______     _______ _    _ ______ __  __        __  __ _       ')
    logging.info('   |  ____|   /\    / ____\ \   / / ____| |  | |  ____|  \/  |      |  \/  | |      ')
    logging.info('   | |__     /  \  | (___  \ \_/ / |    | |__| | |__  | \  / |______| \  / | |      ')
    logging.info('   |  __|   / /\ \  \___ \  \   /| |    |  __  |  __| | |\/| |______| |\/| | |      ')
    logging.info('   | |____ / ____ \ ____) |  | | | |____| |  | | |____| |  | |      | |  | | |____  ')
    logging.info('   |______/_/    \_\_____/   |_|  \_____|_|  |_|______|_|  |_|      |_|  |_|______| ')
    logging.info('                                                                                    ')
    logging.info('####################################################################################')

    MM = ModulManager()

    O_MF = MetricFabricator(Lsettings.Output_metrics, Lsettings.Output_metrics_settings)
    HY_MF = MetricFabricator(Lsettings.Hyperparamter_metric, Lsettings.Hyperparamter_setting)

    ae = Application_env(MM, O_MF, HY_MF, Lsettings, WORKING_PATH=workingPath)

    app = AFE_DM(ae)

    app.start()
    cleanUpWorkdir(workingPath, clean)
    time.sleep(1)


def cleanUpWorkdir(workingPath, clean, outputordner: bool = False):
    path = os.path.join(workingPath, 'TMP')
    if os.path.exists(path):
        print('remove TMP')
        shutil.rmtree(path, True)

    path = os.path.join(workingPath, 'MPI_TRANSFER')
    if os.path.exists(path):
        print('remove MPI_TRANSFER folder')
        shutil.rmtree(path, True)

    path = os.path.join(workingPath, 'catboost_info')
    if os.path.exists(path):
        print('remove catboost_info folder')
        shutil.rmtree(path, True)

    if outputordner:
        if clean:
            print('remove output-folder')
            path = os.path.join(workingPath, 'Output')
            if os.path.exists(path):
                shutil.rmtree(path, True)


def __getAllHJSON(path):
    globstatment = path + '/*.hjson'
    hjsonFiles = glob.glob(globstatment)
    return hjsonFiles


if __name__ == "__main__":
    main()
