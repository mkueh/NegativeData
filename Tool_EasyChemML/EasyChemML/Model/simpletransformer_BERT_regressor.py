from EasyChemML.Utilities.MetricUtilities.Metric import MetricMode
from EasyChemML.Model.Abstract_Model import Abstract_Model
from simpletransformers.classification import (ClassificationModel, ClassificationArgs)
import pandas as pd
from pathlib import Path
import numpy as np
from sklearn.metrics import r2_score
from EasyChemML.Utilities.Application_env import Application_env
import pkg_resources


class simpletransformer_BERT_regressor(Abstract_Model):
    clf = None



    def __init__ (self, param, log_folder:str, APP_ENV:Application_env):
        super().__init__(APP_ENV)
        if 'model_dir' in param.keys():
            bert_path = Path(param.pop('model_dir'))
            bert_path.resolve()
            bert_path = str(bert_path)
        else:
            bert_path = pkg_resources.resource_filename("rxnfp", "models/transformers/bert_pretrained")
        model_args = self._get_default_param(log_folder)
        if 'dropout' in param.keys():
            model_args.config = {'hidden_dropout_prob': param.pop('dropout')}
        device = None
        if 'cuda' in param.keys():
            device = param.pop('cuda')
        model_args.update_from_dict(param)
        if device:
            self.clf = ClassificationModel('bert', bert_path, num_labels=1, cuda_device=device, args=model_args)
        else:
            self.clf = ClassificationModel('bert', bert_path, num_labels=1, args=model_args)

    def _get_default_param(self, log_folder):
        std_params = {'regression': True, 'overwrite_output_dir': True, 'train_batch_size': 32, 'eval_batch_size': 32,
                      'max_seq_length': 512, 'manual_seed': 42}
        model_args = ClassificationArgs()
        model_args.update_from_dict(std_params)
        model_args.output_dir = str(Path(log_folder) / 'Outputs')
        model_args.best_model_dir = str(Path(log_folder) / 'Outputs' / 'best_model')
        model_args.cache_dir = str(Path(log_folder) / 'cache_dir')
        model_args.no_cache = True
        model_args.save_eval_checkpoints = False
        model_args.save_model_every_epoch = False
        model_args.save_optimizer_and_scheduler = False
        return model_args

    def get_param(self) -> dict:
        return self.clf.args.__dict__

    def fit_and_eval(self, X, y, X_test, y_test):
        self.clf.args.evaluate_during_training = True
        self.clf.args.evaluate_during_training_verbose = True
        X = np.ravel(X)
        y = np.ravel(y)
        X_test = np.ravel(X_test)
        y_test = np.ravel(y_test)
        train_data = {'text': X, 'labels': y}
        eval_data = {'text': X_test, 'labels': y_test}
        train_df = pd.DataFrame(train_data).sample(frac=1.0, random_state=42).reset_index(drop=True)
        eval_df = pd.DataFrame(eval_data)
        self.clf.train_model(train_df, eval_df=eval_df, r2=r2_score)

    def predict(self, X):
        X = list(X)
        predictions, raw_output = self.clf.predict(X) #Fehler
        return predictions

    @staticmethod
    def getItemname():
        return "simpletransformer_BERT_regressor"

    @staticmethod
    def getMetricMode():
        return MetricMode.regressor

    @staticmethod
    def hasBatchMode():
        return False
