from typing import List, Optional
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from libsql.db import SessionLocal, Base, engine
from libsql import crud

import pandas as pd

def split_fights(df: pd.DataFrame) -> pd.DataFrame:
    '''
    Reshape DataFrame to split Red/Blue fight stats into their own rows
    '''
    shared  = ['Date', 'Gender', 'WeightClass']
    blue    = []
    red     = []

    renameTo = {}
    for col in df.columns.to_list():
        if col[:3].lower() == "red":
            red.append(col)
            renameTo[col] = col[3:].lower()
        elif col[:4].lower() == "blue":
            blue.append(col)
            renameTo[col] = col[4:].lower()
    
    for col in shared:
        renameTo[col] = col.lower()

    rfighter = df[shared + red].rename(columns=renameTo)
    bfighter = df[shared + blue].rename(columns=renameTo)
    return pd.concat([rfighter, bfighter]).reset_index(drop=True)

def populate_db_bulk(stats_dict, wc_dict, session: Session):
    """
    Efficient bulk insertion method for UFC dataset
    """
    session = SessionLocal()
    
    # Collect all fighter data and perform bulk insertion
    fighter_data = []
    for stats in stats_dict.values():
        fighter_data.append(stats)

    crud.bulk_insert_fighters(session, fighter_data)
        
    # Query the fighters to get their IDs and build weight class rows
    weight_class_data = []
    for fighter_name, weight_classes in wc_dict.items():
        # Find the fighter in the database to get their ID
        fighter = crud.get_fighter_stats(session, fighter_name)
        if not fighter:
            continue

        for wc in weight_classes:
            weight_class_data.append({
                'fighter_id': fighter.id,
                'weightclass': wc
            })
    
    # Bulk insert weight classes
    crud.bulk_insert_weightclass(session, weight_class_data)
    
    session.commit()
    print(f"Bulk inserted {len(fighter_data)} fighters and {len(weight_class_data)} weight class records")

def main():
    SCRIPT_DIR = Path(__file__).resolve().parent
    DATASET_PATH = SCRIPT_DIR.parent / "datasets" / "ufc-clean.csv"

    # Read cleaned data and split stats by fighter
    df = pd.read_csv(DATASET_PATH)
    df = split_fights(df)

    # Convert date column to datetime
    if df['date'].dtype == 'object':
        df['date'] = pd.to_datetime(df['date'])

    # Iterate through dataframe and collect latest fight data
    latest_fights = {}
    wc_unique = defaultdict(set)

    for _, row in df.iterrows():
        name = row['fighter']
        fight_date = row['date']
        weight_class = row['weightclass']  
        
        if pd.notna(weight_class):
            wc_unique[name].add(weight_class)
        
        if name not in latest_fights:
            # First time seeing this fighter
            latest_fights[name] = row.to_dict()
        else:
            # Compare dates to see if this fight is more recent
            curr_date = latest_fights[name]['date']
            if fight_date > curr_date:
                latest_fights[name] = row.to_dict()

    wc_dict = {fighter : list(classes) for fighter, classes in wc_unique.items()}

    # Drop and recreate existing schema, instantiate session
    Base.metadata.drop_all(bind=engine) 
    Base.metadata.create_all(engine)
    session = SessionLocal()

    # Populate Database
    populate_db_bulk(latest_fights, wc_dict, session)

if __name__ == "__main__":
    main()