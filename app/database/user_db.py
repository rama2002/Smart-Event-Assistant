import bcrypt
from app.database.db import execute_query  
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_user(username, email, password, role_id):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    query = '''
    INSERT INTO public.users (username, email, password_hash, role_id)
    VALUES (%s, %s, %s, %s)
    RETURNING user_id, username, email, created_at, role_id;
    '''
    new_user_data = execute_query(query, (username, email, hashed_password.decode('utf-8'), role_id), fetchone=True)
    if new_user_data:
        return {
            "user_id": new_user_data["user_id"],
            "username": new_user_data["username"],
            "email": new_user_data["email"],
            "role_id": new_user_data["role_id"]  
        }
    return None


def update_user(user_id, username=None, email=None, password=None):
    params = []
    query_parts = []
    if username:
        query_parts.append("username = %s")
        params.append(username)
    if email:
        query_parts.append("email = %s")
        params.append(email)
    if password:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        query_parts.append("password_hash = %s")
        params.append(hashed_password)
    
    query = f"UPDATE public.users SET {', '.join(query_parts)} WHERE user_id = %s RETURNING user_id, username, email, created_at, role_id;"
    params.append(user_id)
    return execute_query(query, params, fetchone=True)

def get_user_by_email(email):
    query = "SELECT user_id, username, email, role_id FROM users WHERE email = %s;"
    result = execute_query(query, (email,), fetchone=True)
    if result:
        return {
            "user_id": result['user_id'],
            "username": result['username'],
            "email": result['email'],
            "role_id": result['role_id']
        }
    return None

def authenticate_user(username: str, password: str):
    user_record = get_user_by_username(username)
    if user_record:
        if pwd_context.verify(password, user_record['password_hash']):
            return user_record
    return None

def get_user_by_username(username):
    query = "SELECT user_id, username, email, password_hash, role_id, created_at FROM public.users WHERE username = %s;"
    result = execute_query(query, (username,), fetchone=True)
    if result:
        user_dict = {
            "user_id": result[0],
            "username": result[1],
            "email": result[2],
            "password_hash": result[3],
            "role_id": result[4],
            "created_at": result[5]
        }
        return user_dict
    return None



