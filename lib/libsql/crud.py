from sqlalchemy.orm import Session
from sqlalchemy import insert

from .schema import Fighter, WeightClass

# ----------------------------
# Reads / Common Queries
# ----------------------------

def get_fighter_weight_classes(session: Session, fighter_name: str):
    """
    Query: Get all weight classes a fighter has fought at
    """
    fighter = session.query(Fighter).filter(Fighter.fighter == fighter_name).first()
    if fighter:
        weight_classes = [wc.weight_class for wc in fighter.weight_classes]
        return weight_classes
    return []

def get_fighters_by_weight_class(session: Session, weight_class: str):
    """
    Query: Get all fighters who fought at a specific weight class
    """
    weight_class_records = session.query(WeightClass).filter(
        WeightClass.weight_class == weight_class
    ).all()
    fighters = [wc.fighter for wc in weight_class_records]
    
    return fighters

def get_fighter_stats(session: Session, fighter_name: str): 
    return session.query(Fighter).filter(Fighter.fighter == fighter_name).first()

# ----------------------------
# Writes / Insertions
# ----------------------------

def bulk_insert_fighters(session: Session, fighter_data: list[dict]):
    """
    Bulk insert fighters into database.
    Each entry in fighter_data must match columns of Fighter table
    """
    session.execute(insert(Fighter), fighter_data)
    session.flush()  # ensures IDs get assigned if you need them

def bulk_insert_weightclass(session: Session, wc_data: list[dict]):
    """
    Bulk insert weightclasses into database.
    Each entry in wc_data must match columns of WeightClass table
    """
    session.execute(insert(WeightClass), wc_data)
    session.flush()