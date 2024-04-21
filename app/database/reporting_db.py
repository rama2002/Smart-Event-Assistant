from app.database.db import execute_query

def fetch_event_attendance():
    query = """
    SELECT e.title, COUNT(ae.event_id) as attendee_count
    FROM events e
    JOIN attendee_events ae ON e.event_id = ae.event_id
    GROUP BY e.title
    ORDER BY MIN(e.start_date);
    """
    result = execute_query(query, fetch=True)
    if result:
        return [{'title': row['title'], 'attendee_count': row['attendee_count']} for row in result]
    return []

def fetch_platform_performance():
    query = """
    SELECT date_trunc('month', created_at) as month, COUNT(*) as signups
    FROM users
    GROUP BY 1
    ORDER BY 1;
    """
    results = execute_query(query, fetch=True)
    performance_data = [
        {'month': result['month'], 'signups': result['signups']}
        for result in results
    ]
    return performance_data

