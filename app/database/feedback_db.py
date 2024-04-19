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
    query = "SELECT * FROM questions WHERE event_id = %s;"
    result = execute_query(query, (event_id,), fetch=True)
    return [dict(row) for row in result] if result else []

def get_answers_by_question(question_id):
    query = "SELECT * FROM answers WHERE question_id = %s;"
    result = execute_query(query, (question_id,), fetch=True)
    return [dict(row) for row in result] if result else []
