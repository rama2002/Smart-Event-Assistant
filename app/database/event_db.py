from app.logging_config import get_logger
from app.database.db import execute_query


logger = get_logger(__name__)

def get_event_by_id(event_id):
    query = '''
    SELECT event_id, title, description, start_date, end_date, location, created_by, cover_attachment_id
    FROM events
    WHERE event_id = %s;
    '''
    result = execute_query(query, (event_id,), fetchone=True)
    if result:
        return {
            "event_id": result[0],
            "title": result[1],
            "description": result[2],
            "start_date": result[3].isoformat() if result[3] else None,
            "end_date": result[4].isoformat() if result[4] else None,
            "location": result[5],
            "created_by": result[6],
            "cover_attachment_id": result[7]
        }
    return None


def add_event(title, description, start_date, end_date, location, created_by):
    query = '''
    INSERT INTO events (title, description, start_date, end_date, location, created_by)
    VALUES (%s, %s, %s, %s, %s, %s)
    RETURNING event_id, title, description, start_date, end_date, location;
    '''
    return execute_query(query, (title, description, start_date, end_date, location, created_by), fetchone=True)
  
from app.database.db import execute_query

def update_event(event_id, title=None, description=None, start_date=None, end_date=None, location=None):
    query = '''
    UPDATE events 
    SET title = COALESCE(%s, title),
        description = COALESCE(%s, description),
        start_date = COALESCE(%s, start_date),
        end_date = COALESCE(%s, end_date),
        location = COALESCE(%s, location)
    WHERE event_id = %s
    RETURNING event_id, title, description, start_date, end_date, location, created_by;
    '''
    result = execute_query(query, (title, description, start_date, end_date, location, event_id), fetchone=True)
    
    if result:
        return {
            "event_id": result[0],
            "title": result[1],
            "description": result[2],
            "start_date": result[3],
            "end_date": result[4],
            "location": result[5],
            "created_by": result[6]
        }
    else:
        return None

def delete_event(event_id):
    query = 'DELETE FROM events WHERE event_id = %s RETURNING *;'
    result = execute_query(query, (event_id,), fetchone=True)
    return result

def enroll_in_event(user_id, event_id):
    query = '''
    INSERT INTO attendee_events (user_id, event_id)
    VALUES (%s, %s)
    RETURNING user_id, event_id;
    '''
    result = execute_query(query, (user_id, event_id), fetchone=True)
    return result

def unenroll_in_event(user_id, event_id):
    query = '''
    DELETE FROM attendee_events
    WHERE user_id = %s AND event_id = %s
    RETURNING *;
    '''
    result = execute_query(query, (user_id, event_id), fetchone=True)
    return result

def check_enrollment(user_id, event_id):
    query = '''
    SELECT EXISTS(
        SELECT 1
        FROM attendee_events
        WHERE user_id = %s AND event_id = %s
    );
    '''
    result = execute_query(query, (user_id, event_id), fetchone=True)
    return result[0] if result else False

def fetch_filtered_events(interest_id, title, location, event_date, page_number, page_size, user_id=None):
    parameters = []
    count_base_query = """
    SELECT COUNT(*)
    FROM events e
    LEFT JOIN event_interests ei ON e.event_id = ei.event_id
    WHERE 1=1
    """
    count_query = count_base_query

    events_base_query = """
    SELECT e.event_id, e.title, e.description, e.start_date, e.end_date, e.location, e.created_by, FALSE AS recommended, cover_attachment_id
    FROM events e
    LEFT JOIN event_interests ei ON e.event_id = ei.event_id
    WHERE 1=1
    """
    events_query = events_base_query

    if user_id:
        events_query = """
        SELECT e.event_id, e.title, e.description, e.start_date, e.end_date, e.location, e.created_by,
        CASE WHEN ui.interest_id IS NOT NULL THEN TRUE ELSE FALSE END AS recommended, cover_attachment_id
        FROM events e
        LEFT JOIN event_interests ei ON e.event_id = ei.event_id
        LEFT JOIN user_interests ui ON ui.interest_id = ei.interest_id AND ui.user_id = %s
        WHERE 1=1
        """
    
        count_query = """
        SELECT COUNT(*)
        FROM events e
        LEFT JOIN event_interests ei ON e.event_id = ei.event_id
        LEFT JOIN user_interests ui ON ui.interest_id = ei.interest_id AND ui.user_id = %s
        WHERE 1=1
        """
        parameters.append(user_id)
    
    if interest_id:
        count_query += " AND ei.interest_id = %s"
        events_query += " AND ei.interest_id = %s"
        parameters.append(interest_id)
    
    if title:
        count_query += " AND e.title ILIKE %s"
        events_query += " AND e.title ILIKE %s"
        parameters.append(f'%{title}%')
    
    if location:
        count_query += " AND e.location ILIKE %s"
        events_query += " AND e.location ILIKE %s"
        parameters.append(f'%{location}%')
    
    if event_date:
        count_query += " AND DATE(e.start_date) = %s"
        events_query += " AND DATE(e.start_date) = %s"
        parameters.append(event_date)
    
   
    total_count = execute_query(count_query, parameters, fetchone=True)[0]

    
    offset = (page_number - 1) * page_size
    events_query += " ORDER BY recommended DESC, e.start_date LIMIT %s OFFSET %s"
    parameters.extend([page_size, offset])

    results = execute_query(events_query, parameters, fetch=True)
    events = [
        {
            "event_id": result[0],
            "title": result[1],
            "description": result[2],
            "start_date": result[3],
            "end_date": result[4],
            "location": result[5],
            "created_by": result[6],
            "recommended": result[7],
            "cover_attachment_id": result[8]
        }
        for result in results
    ]

    total_pages = max(1, (total_count + page_size - 1) // page_size)
    return events, total_pages


def get_enrolled_events_for_attendee(user_id):
    query = '''
    SELECT e.event_id, e.title, e.description, e.start_date, e.end_date, e.location, e.cover_attachment_id
    FROM events e
    JOIN attendee_events ae ON e.event_id = ae.event_id
    WHERE ae.user_id = %s
    ORDER BY e.start_date;
    '''
    results = execute_query(query, (user_id,), fetch=True)
    return [
        {
            "event_id": result[0],
            "title": result[1],
            "description": result[2],
            "start_date": result[3],
            "end_date": result[4],
            "location": result[5],
            "cover_attachment_id": result[6]
        }
        for result in results
    ]

def set_event_cover_image(event_id: int, attachment_id: int) -> bool:
    query = """
        UPDATE public.events
        SET cover_attachment_id = %s
        WHERE event_id = %s;
    """
    try:
        execute_query(query, (attachment_id, event_id))
        return True
    except Exception as e:
        print(f"Error setting cover image: {e}")
        return False