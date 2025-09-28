# UFC Predictor

## Objectives
1. Train ML models (including deep learning model in PyTorch) to predict UFC fight card outcomes
2. Host model as a service and deploy in a fullstack application

## Project Architecture
![](/docs/UFC-Predictor-HLD.png)

## Setup Python Virtual Environment

```bash
python3 -m venv <env_name>
source <env_name>/bin/activate
pip freeze > requirements.txt
pip install -r requirements.txt
```

## Project Structure
```
project-root/                                                       
├── app/        → web app code     
├── datasets/   → csv                        
├── docs/       → documentation and project notes        
├── lib/        → custom libraries used across entire repo
├── model/      → ML model API (serves XGB and PyTorch models) 
├── notebooks/  → Jupyter notebooks for exploration & prototyping   
├── scripts/    → helper scripts for automation 
└── README.md   → project overview                                  
```

## Resources

Dataset link (UFC fight stats): https://www.kaggle.com/datasets/mdabbert/ultimate-ufc-dataset/data
