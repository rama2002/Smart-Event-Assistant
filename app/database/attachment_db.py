import psycopg2
from psycopg2 import extras
from app.database.db import create_connection
from app.logging_config import get_logger

logger = get_logger(__name__)

def add_attachment(event_id, file_name, mime_type, file_size, file_content):
    query = '''
    INSERT INTO event_attachments (event_id, file_name, mime_type, file_size, file_content)
    VALUES (%s, %s, %s, %s, %s)
    RETURNING attachment_id;
    '''
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (event_id, file_name, mime_type, file_size, file_content))
            attachment_id = cursor.fetchone()[0]
            conn.commit()
            return {"attachment_id": attachment_id}
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()
    return None

def get_attachment(attachment_id):
    query = 'SELECT attachment_id, event_id, file_name, mime_type, file_size, file_content FROM event_attachments WHERE attachment_id = %s;'
    conn = create_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, (attachment_id,))
            attachment = cursor.fetchone()
            return dict(attachment) if attachment else None
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()
    return None

def delete_attachment(attachment_id):
    query = 'DELETE FROM event_attachments WHERE attachment_id = %s RETURNING attachment_id;'
    conn = create_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(query, (attachment_id,))
            deleted_id = cursor.fetchone()
            conn.commit()
            return {"deleted_attachment_id": deleted_id[0]} if deleted_id else None
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()
    return None


def fetch_attachments_for_event(event_id):
    query = '''
    SELECT attachment_id, event_id, file_name, mime_type, file_size, uploaded_on
    FROM event_attachments
    WHERE event_id = %s;
    '''
    conn = create_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, (event_id,))
            attachments = cursor.fetchall()
            return [dict(attachment) for attachment in attachments] if attachments else []
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        conn.rollback()
    finally:
        conn.close()
    return []
