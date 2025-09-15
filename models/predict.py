import xgboost as xgb
import torch
import torch.nn as nn
import numpy as np
import pickle
from typing import Dict, List, Tuple, Union
import warnings

class UFCPredictor:
    def __init__(self, xgb_model_path: str, pytorch_model_path: str, pytorch_model_class=None):
        """
        Initialize the UFC predictor with both models
        
        Args:
            xgb_model_path: Path to XGBoost model file
            pytorch_model_path: Path to PyTorch model file
            pytorch_model_class: PyTorch model class (if loading state dict)
        """
        self.xgb_model = self.load_xgb_model(xgb_model_path)

        self.pytorch_model = None
        self.pytorch_model_class = pytorch_model_class
        

    def load_xgb_model(self, xgb_path: str):
        try:
            if xgb_path.endswith('.json') or xgb_path.endswith('.ubj'):
                self.xgb_model = xgb.XGBClassifier()
                self.xgb_model.load_model(xgb_path)
            print("XGBoost model loaded successfully")
        except Exception as e:
            print(f"Error loading XGBoost model: {e}")

    def load_torch_model(self, pytorch_path: str):
        pass

    def xgb_vectorize_input():
        pass
    '''
    Index(['RedExpectedValue', 'BlueExpectedValue', 'BlueCurrentWinStreak',
       'BlueAvgSigStrPct', 'BlueAvgTDPct', 'RedAvgSigStrPct', 'RedAvgTDPct',
       'RedLosses', 'RedWinsByDecision', 'RedDaysSinceLastFight',
       'BlueDaysSinceLastFight', 'ExpectedValueDiff', 'CurrentLoseStreakDiff',
       'CurrentWinStreakDiff', 'AvgSigStrLandedDiff', 'AvgSubAttDiff',
       'AvgTDLandedDiff', 'LossesDiff', 'TotalRoundsFoughtDiff',
       'ReachCmsDiff', 'WeightLbsDiff', 'AgeDiff', 'DaysSinceLastFightDiff',
       'CurrELODiff'],
      dtype='object')
    '''


'''
We'll initially keep this file as a CLI tool to test querying
our UFC prediction models and getting bet outcomes.

# TODO
Figure out the best way to host this model:
1) potentially a FastAPI service
2) Keep model in memory with webapp
3) Some other type of model hosting method
'''
if __name__ == "__main__":
    pass