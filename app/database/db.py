import psycopg2
from psycopg2 import OperationalError
from app.config import DB_USER, DB_PASSWORD, DB_HOST, DB_NAME  
from app.logging_config import get_logger
import psycopg2.extras
logger = get_logger(__name__)

def create_connection():
    conn = None
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        logger.info("Connection to PostgreSQL DB successful")
    except OperationalError as e:
        logger.error(f"The error '{e}' occurred")
    return conn


def execute_query(query, params=None, fetch=False, fetchone=False):
    conn = create_connection()
    if conn is not None:
        try:
            with conn:
                with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                    cur.execute(query, params)
                    if fetch:
                        result = cur.fetchall()
                        return result
                    if fetchone:
                        result = cur.fetchone()
                        return result
        except psycopg2.Error as e:
            logger.error(f"Database error: {e}")
        finally:
            conn.close()
    return None