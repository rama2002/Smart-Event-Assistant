from app.database.event_db import execute_query
from app.logging_config import get_logger

logger = get_logger(__name__)


def add_speaker(name: str):
    query = 'INSERT INTO speakers (name) VALUES (%s) RETURNING speaker_id;'
    result = execute_query(query, (name,), fetchone=True)
    if result:
        return result[0]  
    else:
        return None


def delete_speaker(speaker_id: int):
    query = 'DELETE FROM speakers WHERE speaker_id = %s RETURNING speaker_id;'
    return execute_query(query, (speaker_id,), fetchone=True)

def get_all_speakers():
    query = 'SELECT speaker_id, name FROM speakers;'
    results = execute_query(query, fetch=True)
    if results:
       
        return [dict(result) for result in results]
    else:
        return None



