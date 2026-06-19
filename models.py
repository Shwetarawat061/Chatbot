import mysql.connector
from mysql.connector import pooling
from config import Config

db_config = {
    "host": Config.DB_HOST,
    "user": Config.DB_USER,
    "password": Config.DB_PASSWORD,
    "database": Config.DB_NAME
}

# Use connection pooling to handle multiple requests efficiently
try:
    db_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="mypool", pool_size=5, **db_config
    )
except mysql.connector.Error as err:
    print(f"Error establishing DB connection pool: {err}")
    db_pool = None

def get_db_connection():
    if db_pool:
        return db_pool.get_connection()
    return mysql.connector.connect(**db_config)

class UserModel:
    @staticmethod
    def create_user(username, email, password_hash):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                (username, email, password_hash)
            )
            conn.commit()
            return cursor.lastrowid
        except mysql.connector.Error:
            return None
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def find_by_username(username):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user

    @staticmethod
    def update_profile(user_id, username, profile_pic=None):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        if profile_pic:
            cursor.execute(
                "UPDATE users SET username = %s, profile_pic = %s WHERE id = %s",
                (username, profile_pic, user_id)
            )
        else:
            cursor.execute(
                "UPDATE users SET username = %s WHERE id = %s",
                (username, user_id)
            )
        conn.commit()
        cursor.close()
        conn.close()

class ChatModel:
    @staticmethod
    def create_session(user_id, title="New Chat"):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("INSERT INTO chat_sessions (user_id, title) VALUES (%s, %s)", (user_id, title))
        conn.commit()
        sid = cursor.lastrowid
        cursor.close()
        conn.close()
        return sid

    @staticmethod
    def get_user_sessions(user_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM chat_sessions WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        sessions = cursor.fetchall()
        cursor.close()
        conn.close()
        return sessions

    @staticmethod
    def save_message(session_id, sender, message_text, sentiment='Neutral'):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "INSERT INTO messages (session_id, sender, message_text, sentiment) VALUES (%s, %s, %s, %s)",
            (session_id, sender, message_text, sentiment)
        )
        conn.commit()
        cursor.close()
        conn.close()

    @staticmethod
    def get_session_messages(session_id):
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM messages WHERE session_id = %s ORDER BY timestamp ASC", (session_id,))
        messages = cursor.fetchall()
        cursor.close()
        conn.close()
        return messages
