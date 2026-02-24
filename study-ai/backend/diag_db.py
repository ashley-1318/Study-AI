import os
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./studyai.db"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
db = Session()

try:
    # Check current state of 'Stateful Agents'
    res = db.execute(text("SELECT id, name, material_id, mastery_score, repetition_count FROM concepts WHERE name LIKE '%Stateful Agents%'")).fetchall()
    print("--- CONCEPTS ---")
    for row in res:
        print(row)
    
    # Check learning events
    res = db.execute(text("SELECT event_type, concept_id, result, timestamp FROM learning_events ORDER BY timestamp DESC LIMIT 10")).fetchall()
    print("\n--- RECENT EVENTS ---")
    for row in res:
        print(row)
finally:
    db.close()
