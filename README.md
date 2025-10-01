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
pip install -e lib
```

## Useful Docker Commands

```bash
docker compose --env-file .env.dev up --build --detach
docker compose down
docker ps
docker stop <container_id>
docker rm <container_id>
```

## Project Structure
```
project-root/    
├── models/     → save models to disk here                                               
├── datasets/   → csv                        
├── docs/            
├── notebooks/  → Jupyter notebooks for exploration & prototyping   
├── scripts/    → automation tasks
├── lib/        
|   ├── libsql/     → define UFC DB and SQL queries
|   ├── ufcpredict/ → load and query ML models
└── README.md   → project overview                                  
```

## Resources

Dataset link (UFC fight stats): https://www.kaggle.com/datasets/mdabbert/ultimate-ufc-dataset/data
