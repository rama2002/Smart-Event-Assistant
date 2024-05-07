from typing import List
from app.database.event_db import execute_query
from app.logging_config import get_logger

logger = get_logger(__name__)

def add_interest(name):
    query = 'INSERT INTO interests (name) VALUES (%s) RETURNING interest_id;'
    result = execute_query(query, (name,), fetchone=True)
    if result:
        return result['interest_id']
    else:
        return None

def delete_interest(interest_id):
    query = 'DELETE FROM interests WHERE interest_id = %s;'
    execute_query(query, (interest_id,))

def update_interest(interest_id: int, name: str):
    query = 'UPDATE interests SET name = %s WHERE interest_id = %s RETURNING *;' 
    data = (name, interest_id)  
    result = execute_query(query, data, fetchone=True)  
    return result

def add_user_interest(user_id: int, interest_id: int) -> bool:
   
    query = """
    INSERT INTO user_interests (user_id, interest_id)
    VALUES (%s, %s);
    """
    try:
        execute_query(query, (user_id, interest_id))
        return True 
    except Exception as e:
       
        logger.error(f"Failed to add interest for user: {e}")
        return False 

def delete_user_interest(user_id: int, interest_id: int) -> bool:
    query = '''
    DELETE FROM user_interests
    WHERE user_id = %s AND interest_id = %s;
    '''
    execute_query(query, (user_id, interest_id))

    return True

def get_user_interests(user_id: int) -> List[int]:
    query = '''
    SELECT interest_id FROM user_interests
    WHERE user_id = %s;
    '''
    results = execute_query(query, (user_id,), fetch=True)
    return [result['interest_id'] for result in results] if results else []

def add_event_interest(event_id: int, interest_id: int) -> bool:
    query = """
    INSERT INTO event_interests (event_id, interest_id)
    VALUES (%s, %s);
    """
    try:
        execute_query(query, (event_id, interest_id))
        return True
    except Exception as e:
        logger.error(f"Failed to add interest to event: {e}")
        return False

def delete_event_interest(event_id: int, interest_id: int) -> bool:
    query = """
    DELETE FROM event_interests
    WHERE event_id = %s AND interest_id = %s;
    """
    try:
        execute_query(query, (event_id, interest_id))
        return True
    except Exception as e:
        logger.error(f"Failed to delete interest from event: {e}")
        return False

def get_all_interests():
    query = "SELECT interest_id, name FROM interests;"
    results = execute_query(query, fetch=True)
    if results:
        return [
            {
                "interest_id": result['interest_id'],
                "name": result['name']
            }
            for result in results
        ]
    return []

def get_event_interests(event_id: int):
    query = """
    SELECT i.interest_id, i.name
    FROM interests i
    JOIN event_interests ei ON ei.interest_id = i.interest_id
    WHERE ei.event_id = %s;
    """
    results = execute_query(query, (event_id,), fetch=True)
    if results:
        return [
            {
                "interest_id": result['interest_id'],
                "name": result['name']
            }
            for result in results
        ]
    return []
