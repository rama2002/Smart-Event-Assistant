import psycopg2
from psycopg2 import sql
from app.logging_config import get_logger
from app.database.db import create_connection


logger = get_logger(__name__)

def execute_query(query, data=None, fetch=False, fetchone=False):
    conn = create_connection()
    if conn is not None:
        try:
            with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor: 
                if data is None:
                    cursor.execute(query)
                else:
                    cursor.execute(query, data if isinstance(data, tuple) else tuple(data))
                
                if fetch:
                    result = cursor.fetchall()
                elif fetchone:
                    result = cursor.fetchone()
                else:
                    result = None
                conn.commit()
                return result
        except psycopg2.Error as e:
            logger.error(f"The error '{e}' occurred")
            conn.rollback()
        finally:
            conn.close()
    else:
        logger.error("No connection to the database.")
    return None


def add_event(title, description, start_date, end_date, location, created_by):
    query = '''
    INSERT INTO events (title, description, start_date, end_date, location, created_by)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING event_id, title, description, start_date, end_date, location;
    '''
    return execute_query(query, (title, description, start_date, end_date, location, created_by), fetchone=True)
  
def update_event(event_id, title=None, description=None, start_date=None, end_date=None, location=None):
    conn = create_connection() 
    if conn is not None:
        try:
            fields = {
                "title": title,
                "description": description,
                "start_date": start_date,
                "end_date": end_date,
                "location": location
            }
            set_clause = sql.SQL(", ").join(
                sql.Identifier(k) + sql.SQL(" = ") + sql.Placeholder(k) for k, v in fields.items() if v is not None
            )
            query = sql.SQL("UPDATE events SET {set_clause} WHERE event_id = {id} RETURNING *").format(
                set_clause=set_clause,
                id=sql.Literal(event_id)
            )
            cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cursor.execute(query.as_string(conn), fields)
            result = cursor.fetchone()
            conn.commit()
            return dict(result) if result else None
        except psycopg2.Error as e:
            logger.error(f"The error '{e}' occurred")
            conn.rollback()
        finally:
            conn.close()
    else:
        logger.error("No connection to the database.")
    return None



def delete_event(event_id):
    query = 'DELETE FROM events WHERE event_id = %s RETURNING *;'
    result = execute_query(query, (event_id,), fetchone=True)
    return result

def enroll_in_event(user_id, event_id):
    query = '''
    INSERT INTO user_events (user_id, event_id)
    VALUES (%s, %s);
    '''
    execute_query(query, (user_id, event_id))

def unenroll_in_event(user_id, event_id):
    query = '''
    DELETE FROM user_events
    WHERE user_id = %s AND event_id = %s
    RETURNING *;
    '''
    result = execute_query(query, (user_id, event_id), fetchone=True)
    return result

def fetch_filtered_events(interest_id, title, location, event_date, page_number, page_size):
    query = """
    SELECT e.event_id, e.title, e.description, e.start_date, e.end_date, e.location, e.created_by FROM events e
    LEFT JOIN event_interests ei ON e.event_id = ei.event_id
    WHERE 1=1
    """
    parameters = []

    if interest_id:
        query += " AND ei.interest_id = %s"
        parameters.append(interest_id)
    if title:
        query += " AND e.title ILIKE %s"
        parameters.append(f'%{title}%')
    if location:
        query += " AND e.location ILIKE %s"
        parameters.append(f'%{location}%')
    if event_date:
        query += " AND DATE(e.start_date) = %s"
        parameters.append(event_date)

    query += " ORDER BY e.start_date LIMIT %s OFFSET %s"
    offset = (page_number - 1) * page_size
    parameters.extend([page_size, offset])

   
    results = execute_query(query, parameters, fetch=True)
    return results


