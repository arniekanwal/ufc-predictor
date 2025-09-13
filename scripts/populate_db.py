from typing import List, Optional
from collections import defaultdict
from datetime import datetime

from sqlalchemy import create_engine, insert
from sqlalchemy import String, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.orm import Session, sessionmaker

import pandas as pd

class Base(DeclarativeBase):
    pass

class Fighter(Base):
    __tablename__ = "fighters"
    
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    fighter: Mapped[str] = mapped_column(String(35), nullable=False)
    
    # One-to-Many relationship to weightclasses
    weight_classes: Mapped[list["WeightClass"]] = relationship(back_populates="fighter", cascade="all, delete-orphan")

    date = mapped_column(DateTime)
    gender: Mapped[str] = mapped_column(String(6))
    expectedvalue: Mapped[float] = mapped_column(Float)
    currentlosestreak: Mapped[int] = mapped_column(Integer)
    currentwinstreak: Mapped[int] = mapped_column(Integer)
    draws: Mapped[int] = mapped_column(Integer)
    avgsigstrlanded: Mapped[float] = mapped_column(Float)
    avgsigstrpct: Mapped[float] = mapped_column(Float)
    avgsubatt: Mapped[float] = mapped_column(Float)
    avgtdlanded: Mapped[float] = mapped_column(Float)
    avgtdpct: Mapped[float] = mapped_column(Float)
    losses: Mapped[int] = mapped_column(Integer)
    totalroundsfought: Mapped[int] = mapped_column(Integer)
    totaltitlebouts: Mapped[int] = mapped_column(Integer)
    winsbysubmission: Mapped[int] = mapped_column(Integer)
    wins: Mapped[int] = mapped_column(Integer)
    stance: Mapped[str] = mapped_column(String(10), nullable=True)
    heightcms: Mapped[float] = mapped_column(Float)
    reachcms: Mapped[float] = mapped_column(Float)
    weightlbs: Mapped[int] = mapped_column(Integer)
    age: Mapped[int] = mapped_column(Integer)
    winsbydecision: Mapped[int] = mapped_column(Integer)
    winsbykotko: Mapped[int] = mapped_column(Integer)
    ufc_debut: Mapped[int] = mapped_column(Integer)
    dayssincelastfight: Mapped[int] = mapped_column(Integer)
    currelo: Mapped[float] = mapped_column(Float)

    def __repr__(self) -> str:
        return f"<Fighter(id={self.id}, name='{self.fighter}')"
    
class WeightClass(Base):
    __tablename__ = "weight_classes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    
    # Establish Foreign Key to link to Fighter table
    fighter_id: Mapped[int] = mapped_column(ForeignKey('fighters.id'), nullable=False)
    # Back reference to the fighter (create relationship)
    fighter: Mapped["Fighter"] = relationship("Fighter", back_populates="weight_classes")
    
    weightclass: Mapped[str] = mapped_column(String(30), nullable=False)

    def __repr__(self):
        return f"<WeightClass(id={self.id}, fighter_id={self.fighter_id}, weight_class='{self.weight_class}')>"

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

def populate_db_bulk(stats_dict, wc_dict, engine):
    """
    Efficient bulk insertion method for UFC dataset
    """
    Session = sessionmaker(bind=engine)
    
    with Session() as session:
        fighter_data = []

        for stats in stats_dict.values():
            fighter_data.append(stats)
        
        # Bulk insert the fighter data
        session.execute(insert(Fighter), fighter_data)
        session.flush()
        
        # Query back the fighters to get their IDs for weight class insertion
        weight_class_data = []
        for fighter_name, weight_classes in wc_dict.items():
            # Find the fighter in the database to get their ID
            fighter = session.query(Fighter).filter(Fighter.fighter == fighter_name).first()
            if not fighter:
                continue

            for wc in weight_classes:
                weight_class_data.append({
                    'fighter_id': fighter.id,
                    'weightclass': wc
                })
        
        # Bulk insert weight classes
        if weight_class_data:
            session.execute(insert(WeightClass), weight_class_data)
        
        session.commit()
        print(f"Bulk inserted {len(fighter_data)} fighters and {len(weight_class_data)} weight class records")
        

def get_fighter_weight_classes(session, fighter_name):
    """
    Query: Get all weight classes a fighter has fought at
    """
    fighter = session.query(Fighter).filter(Fighter.fighter_name == fighter_name).first()
    if fighter:
        weight_classes = [wc.weight_class for wc in fighter.weight_classes]
        return weight_classes
    return []

def get_fighters_by_weight_class(session, weight_class_name):
    """
    Query: Get all fighters who fought at a specific weight class
    """
    # Method 1: Query WeightClass and access fighters through relationship
    weight_class_records = session.query(WeightClass).filter(
        WeightClass.weight_class == weight_class_name
    ).all()
    fighters = [wc.fighter for wc in weight_class_records]
    
    return fighters

def main():
    # Read cleaned data and split stats by fighter
    df = pd.read_csv('../datasets/ufc-clean.csv')
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
    
    # Initiate session and create schema
    DATABASE_URL = 'sqlite:///../ufc.db'
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

    # Populate Database
    populate_db_bulk(latest_fights, wc_dict, engine)

if __name__ == "__main__":
    main()