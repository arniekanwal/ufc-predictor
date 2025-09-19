import xgboost as xgb
import torch
import torch.nn as nn
import numpy as np
import pickle
from typing import Dict, List, Tuple, Union
import warnings

from pathlib import Path

from libsql.db import SessionLocal
from libsql import crud

class UFCPredictor:
    def __init__(self, xgb_model_file: str, pytorch_model_file: str = None, pytorch_model_class=None):
        """
        Initialize the UFC predictor with multiple models
        
        Args:
            xgb_model_path: XGBoost model filename
            pytorch_model_path: PyTorch model filename
            pytorch_model_class: PyTorch model class (if loading state dict)
        """
        
        PROJECT_ROOT   = Path(__file__).resolve().parents[1]
        self.XGB_PATH       = PROJECT_ROOT / "models" / xgb_model_file
        # TORCH_PATH      = PROJECT_ROOT / "models" / pytorch_model_file

        self.xgb_model = xgb.XGBClassifier()
        self.xgb_model.load_model(self.XGB_PATH)

        self.pytorch_model = None
        self.pytorch_model_class = pytorch_model_class

        self.sesh = SessionLocal()

    # ---------------------------------
    # XGBoost specific methods...
    # ---------------------------------
    
    def xgb_predict(self, fighter1: str, fighter2: str):
        '''
        Build feature vector from input and query XGB model for a prediction

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
        
        print(f"xgb_predict({fighter1}, {fighter2}) was called...")
        r = crud.get_fighter_stats(self.sesh, fighter1)
        b = crud.get_fighter_stats(self.sesh, fighter2)

        # swap the corners based on who has a higher ELO
        if b.currelo > r.currelo: 
            r, b = b, r

        # Build the input vector
        vec = np.array([
            r.expectedvalue,
            b.expectedvalue,
            b.currentwinstreak,
            b.avgsigstrpct,
            b.avgtdpct,
            r.avgsigstrpct,
            r.avgtdpct,
            r.losses,
            r.winsbydecision,
            r.dayssincelastfight,
            b.dayssincelastfight,
            r.expectedvalue - b.expectedvalue,
            r.currentlosestreak - b.currentlosestreak,
            r.currentwinstreak - b.currentwinstreak,
            r.avgsigstrlanded - b.avgsigstrlanded,
            r.avgsubatt - b.avgsubatt,
            r.avgtdlanded - b.avgtdlanded,
            r.losses - b.losses,
            r.totalroundsfought - b.totalroundsfought,
            r.reachcms - b.reachcms,
            r.weightlbs - b.weightlbs,
            r.age - b.age,
            r.dayssincelastfight - b.dayssincelastfight,
            r.currelo - b.currelo
        ]).reshape(1, -1) # Reshape into (1, 24) column vec

        pred = self.xgb_model.predict(vec)
        prob = self.xgb_model.predict_proba(vec)
        print("Prediction Result:")
        print(pred) # 0: Blue winner, 1: Red winner
        print(prob) # [blue_prob, red_prob]
        
    # ---------------------------------
    # PyTorch specific methods...
    # ---------------------------------

    def _load_torch_model(self, pytorch_path: str):
        pass

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
    mmabet = UFCPredictor('ufc_xgb_model.ubj')
    mmabet.xgb_predict("Tom Aspinall", "Jon Jones")