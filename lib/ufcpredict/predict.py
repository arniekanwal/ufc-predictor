import numpy as np
import xgboost as xgb
from pathlib import Path
import os

from libsql.db import SessionLocal
from libsql import crud

class UFCPredictor:
    def __init__(self, xgb_model_file: str = None, pytorch_model_file: str = None, pytorch_model_class=None):
        """
        Initialize the UFC predictor with multiple models
        
        Args:
            xgb_model_path: XGBoost model filename
            pytorch_model_path: PyTorch model filename
            pytorch_model_class: PyTorch model class (if loading state dict)
        """

        # Resolve models directory
        default_models_dir = Path(__file__).resolve().parents[2] / "models"
        self.models_dir = Path(os.getenv("MODELS_DIR", default_models_dir))

        # --- XGBoost model ---
        # First, get the model name (either user supplied or use default)
        if not xgb_model_file:
            xgb_model_file = "ufc_xgb_model.ubj"

        self.XGB_PATH = self.models_dir / xgb_model_file
        if not self.XGB_PATH.exists():
            raise FileNotFoundError(f"XGBoost model not found at {self.XGB_PATH}")

        self.xgb_model = xgb.XGBClassifier()
        self.xgb_model.load_model(self.XGB_PATH)

        # --- PyTorch model ---
        self.pytorch_model = None
        self.pytorch_model_class = pytorch_model_class
        # if pytorch_model_file and pytorch_model_class:
        #     torch_path = self.models_dir / pytorch_model_file
        #     if not torch_path.exists():
        #         raise FileNotFoundError(f"PyTorch model not found at {torch_path}")

        #     self.pytorch_model = pytorch_model_class()
        #     state_dict = torch.load(torch_path, map_location=torch.device("cpu"))
        #     self.pytorch_model.load_state_dict(state_dict)
        #     self.pytorch_model.eval()
        
        # --- DB Session ---
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