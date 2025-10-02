from fastapi import FastAPI
from pydantic import BaseModel

from contextlib import asynccontextmanager
from ufcpredict.predict import UFCPredictor

# Global dict to store models
ml_models = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize your predictor (adjust model path as needed)
    ml_models["xgb"] = UFCPredictor()    
    yield
    # Clean up the ML models and release the resources
    ml_models.clear()

# Create FastAPI app with lifespan events
app = FastAPI(
    title="UFC Fight Predictor API",
    description="API for predicting UFC fight outcomes using machine learning",
    version="1.0.0",
    lifespan=lifespan
)

# ---------------------------
# Pydantic models 
# ---------------------------
class HealthCheck(BaseModel):
    xgb_status: int
    torch_status: int
    version: str

class Prediction(BaseModel):
    fighter1: str
    fighter2: str
    autoselect_corner: bool = False

# ---------------------------
# API Endpoints
# ---------------------------

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "description": "API layer for UFC Predictor",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    return HealthCheck(
        xgb_status = 1 if ml_models.get("xgb") else 0,
        torch_status = 1 if ml_models.get("torch") else 0,
        version="1.0.0"
    )

@app.post("/predict")
def predict(matchup: Prediction):
    model = ml_models["xgb"]
    result = model.xgb_predict(matchup.fighter1, matchup.fighter2, pick_corner=True)
    return result

'''
Examples:
curl -X POST 127.0.0.1:4000/predict -H "Content-Type: application/json" -d '{"fighter1": "Tom Aspinall", "fighter2": "Jon Jones"}'
'''

