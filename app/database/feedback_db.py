from app.database.db import execute_query

def add_question(event_id, user_id, question_text):
    query = "INSERT INTO questions (event_id, user_id, question_text) VALUES (%s, %s, %s) RETURNING *;"
    result = execute_query(query, (event_id, user_id, question_text), fetchone=True)
    return dict(result) if result else None

def add_answer(question_id, user_id, answer_text):
    query = "INSERT INTO answers (question_id, user_id, answer_text) VALUES (%s, %s, %s) RETURNING *;"
    result = execute_query(query, (question_id, user_id, answer_text), fetchone=True)
    return dict(result) if result else None

def get_questions_by_event(event_id):
    query = """
        SELECT q.question_id, q.event_id, q.question_text, u.username AS asked_by, q.asked_on
        FROM questions q
        JOIN users u ON q.user_id = u.user_id
        WHERE q.event_id = %s;
    """
    result = execute_query(query, (event_id,), fetch=True)
    return [dict(row) for row in result] if result else []

def get_answers_by_question(question_id):
    query = """
        SELECT a.answer_id, a.question_id, a.answer_text, u.username AS answered_by, a.answered_on
        FROM answers a
        JOIN users u ON a.user_id = u.user_id
        WHERE a.question_id = %s;
    """
    result = execute_query(query, (question_id,), fetch=True)
    return [dict(row) for row in result] if result else []

def add_rating(event_id, user_id, rating):
    query = """
        INSERT INTO feedback (event_id, user_id, rating)
        VALUES (%s, %s, %s)
        ON CONFLICT (event_id, user_id) DO UPDATE
        SET rating = EXCLUDED.rating
        RETURNING *;
    """
    result = execute_query(query, (event_id, user_id, rating), fetchone=True)
    return dict(result) if result else None

def get_event_rating_summary(event_id):
    query = """
        SELECT AVG(rating) as average_rating, COUNT(*) as rating_count
        FROM feedback
        WHERE event_id = %s;
    """
    result = execute_query(query, (event_id,), fetchone=True)
    return dict(result) if result else None

def get_user_event_rating(event_id, user_id):
    query = """
        SELECT rating FROM feedback
        WHERE event_id = %s AND user_id = %s
    """
    result = execute_query(query, (event_id, user_id), fetchone=True)
    return dict(result) if result else None

def get_questions_and_answers_by_event(event_id):
    query = """
        SELECT q.question_id, q.question_text, u1.username AS asked_by, a.answer_text, u2.username AS answered_by
        FROM questions q
        JOIN users u1 ON q.user_id = u1.user_id
        LEFT JOIN answers a ON q.question_id = a.question_id
        LEFT JOIN users u2 ON a.user_id = u2.user_id
        WHERE q.event_id = %s
        ORDER BY q.question_id, a.answered_on;
    """
    result = execute_query(query, (event_id,), fetch=True)
    return [dict(row) for row in result] if result else []