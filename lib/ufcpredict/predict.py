import numpy as np
import xgboost as xgb
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
        
        self.ROOT       = self._find_project_root()
        self.XGB_PATH   = self.ROOT / "models" / xgb_model_file
        # self.TORCH_PATH = self.ROOT / "models" / pytorch_model_file

        self.xgb_model = xgb.XGBClassifier()
        self.xgb_model.load_model(self.XGB_PATH)

        self.pytorch_model = None
        self.pytorch_model_class = pytorch_model_class

        self.sesh = SessionLocal()

    def _find_project_root(self):
        # Start from current working directory and walk up
        current = Path.cwd()
        while current != current.parent:
            if (current / "models").exists():
                return current
            current = current.parent
        raise FileNotFoundError("Could not find project root with models/ directory")

    # ---------------------------------
    # XGBoost specific methods...
    # ---------------------------------
    
    def xgb_predict(self, fighter1: str, fighter2: str, pick_corner: bool = False):
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

        r = crud.get_fighter_stats(self.sesh, fighter1)
        b = crud.get_fighter_stats(self.sesh, fighter2)

        # swap the corners based on who has a higher ELO
        if pick_corner and b.currelo > r.currelo: 
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
        prob = self.xgb_model.predict_proba(vec).tolist()
        r_p, b_p = prob[0][1], prob[0][0]

        result = {
            "winner": r.fighter if (pred[0] == 1) else b.fighter,
            "rprob": round(r_p, 4),
            "bprob": round(b_p, 4),
            "rcorner": r.fighter,
            "bcorner": b.fighter
        }
        return result
        
    # ---------------------------------
    # PyTorch specific methods...
    # ---------------------------------

    def _load_torch_model(self, pytorch_path: str):
        pass

'''
# TODO:
1) explore xgb.DMatrix
2) add weightclass filters
    --> (i.e. refuse predictions for flyweight vs heavyweight)
'''